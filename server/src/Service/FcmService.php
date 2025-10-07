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

    public function sendNotification(string $token, string $title, string $body): array
    {
        try {
            $accessToken = $this->getAccessToken();
            $url = sprintf('projects/%s/messages:send', $this->projectId);

            $response = $this->client->post($url, [
                'headers' => [
                    'Authorization' => 'Bearer ' . $accessToken,
                    'Content-Type'  => 'application/json',
                ],
                'json' => [
                    'message' => [
                        'token' => $token,
                        'notification' => [
                            'title' => $title,
                            'body'  => $body,
                        ],
                    ],
                ],
            ]);

            $data = json_decode((string)$response->getBody(), true);

            return [
                'success' => true,
                'status' => $response->getStatusCode(),
                'messageId' => $data['name'] ?? null,
            ];
        } catch (\Throwable $e) {
            return [
                'success' => false,
                'error' => $e->getMessage(),
            ];
        }
    }
}
