<?php

namespace App\Service;

use GuzzleHttp\Client;
use Google\Auth\Credentials\ServiceAccountCredentials;

class FcmService
{
    private Client $client;
    private ServiceAccountCredentials $credentials;
    private string $projectId;

    public function __construct(string $projectId, string $serviceAccountPath)
    {
        $this->projectId = $projectId;
        # print content of service account path
        if (!file_exists($serviceAccountPath)) {
            throw new \RuntimeException("Service account file not found: $serviceAccountPath");
        }
        $this->credentials = new ServiceAccountCredentials(
            ['https://www.googleapis.com/auth/firebase.messaging'],
            $serviceAccountPath
        );

        $this->client = new Client([
            'base_uri' => 'https://fcm.googleapis.com/v1/',
        ]);
    }

    private function getAccessToken(): string
    {
        $token = $this->credentials->fetchAuthToken();
        if (!isset($token['access_token'])) {
            throw new \RuntimeException('Failed to fetch Google access token');
        }
        return $token['access_token'];
    }

    /**
     * === OLD ===
     * sendNotification() keeps existing but will not be used
     */

    /**
     * === NEW: Pure data message ===
     * Sends a data-only FCM message (NO notification section).
     * This ensures onMessageReceived() fires even if the app is backgrounded or killed.
     */
    public function sendDataMessage(string $token, array $data): array
    {
        $accessToken = null;
        $url = sprintf('projects/%s/messages:send', $this->projectId);

        try {
            $accessToken = $this->getAccessToken();

            $payload = [
                'message' => [
                    'token' => $token,
                    'data'  => $data,
                    'android' => [
                        'priority' => 'HIGH',
                    ],
                ]
            ];

            error_log("FCM: sending to URL = $url");
            error_log("FCM: token (first 10 chars) = " . substr($token, 0, 10) . "...");
            error_log("FCM: payload = " . json_encode($payload));

            $response = $this->client->post($url, [
                'headers' => [
                    'Authorization' => 'Bearer ' . $accessToken,
                    'Content-Type'  => 'application/json',
                ],
                'json' => $payload,
                'http_errors' => false,  // <-- important: let us inspect 404 manually
            ]);

            $status = $response->getStatusCode();
            $body   = (string)$response->getBody();

            error_log("FCM response status: $status");
            error_log("FCM response body: $body");

            // Handle errors explicitly
            if ($status < 200 || $status >= 300) {
                return [
                    'success' => false,
                    'status'  => $status,
                    'error'   => $body ?: "Unknown error from FCM",
                ];
            }

            $responseData = json_decode($body, true);

            return [
                'success'   => true,
                'status'    => $status,
                'messageId' => $responseData['name'] ?? null,
                'response'  => $responseData,
            ];

        } catch (\GuzzleHttp\Exception\ClientException $e) {
            // 4xx errors
            error_log("FCM ClientException: " . $e->getMessage());
            return [
                'success' => false,
                'error'   => "ClientException: " . $e->getMessage(),
            ];

        } catch (\GuzzleHttp\Exception\ServerException $e) {
            // 5xx errors
            error_log("FCM ServerException: " . $e->getMessage());
            return [
                'success' => false,
                'error'   => "ServerException: " . $e->getMessage(),
            ];
        } catch (\Throwable $e) {
            // Any other error
            error_log("FCM Exception: " . $e->getMessage());
            return [
                'success' => false,
                'error'   => "Exception: " . $e->getMessage(),
            ];
        }
    }
}
