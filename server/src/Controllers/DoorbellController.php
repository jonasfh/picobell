<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use App\Service\FcmService;
use Medoo\Medoo;

class DoorbellController
{
    private Medoo $db;
    private FcmService $fcm;

    public function __construct(Medoo $db)
    {
        $this->db = $db;
        $this->fcm = new FcmService(
            getenv('FIREBASE_PROJECT_ID'),
            __DIR__ . '/../../' . getenv('SERVICE_ACCOUNT_PATH')
        );
    }

    public function ring(Request $req, Response $res): Response
    {
        $body = $req->getParsedBody();
        $serial = $body['pico_serial'] ?? null;

        if (!$serial) {
            return $this->error($res, 'Missing pico_serial', 400);
        }

        // Finn leiligheten som Pico hører til
        $apartment = $this->db->get("apartments", "*", [
            "pico_serial" => $serial
        ]);

        if (!$apartment) {
            return $this->error($res, 'Unknown pico_serial', 404);
        }

        // Finn alle brukere koblet til denne leiligheten via pivot-tabellen
        $userIds = $this->db->select("user_apartment", "user_id", [
            "apartment_id" => $apartment['id']
        ]);

        if (empty($userIds)) {
            return $this->error($res, 'No users linked to apartment', 404);
        }

        // Finn alle aktive devices for disse brukerne
        $devices = $this->db->select("devices", ["token"], [
            "user_id" => $userIds
        ]);

        if (empty($devices)) {
            return $this->error($res, 'No active devices for this apartment', 404);
        }

        $sent = 0;
        $failed = 0;

        foreach ($devices as $d) {
            try {
                $result = $this->fcm->sendNotification(
                    $d['token'],
                    'Ring på døra!',
                    'Noen står utenfor ' . ($apartment['name'] ?? 'inngangen') . ' 🚪🔔',
                    ['apartment_id' => (string)$apartment['id']] // Send apartment_id as string in data payload
                );

                // Firebase returnerer vanligvis {"name": "..."} ved suksess
                if (!empty($result['name'])) {
                    $sent++;
                } else {
                    $failed++;
                }
            } catch (\Throwable $e) {
                error_log("FCM send failed: " . $e->getMessage());
                $failed++;
            }
        }

        $payload = [
            'message' => 'Notifications sent',
            'apartment_id' => $apartment['id'],
            'sent' => $sent,
            'failed' => $failed,
        ];

        $res->getBody()->write(json_encode($payload, JSON_UNESCAPED_UNICODE));
        return $res->withHeader('Content-Type', 'application/json');
    }

    private function error(Response $res, string $msg, int $code): Response
    {
        $res->getBody()->write(json_encode(['error' => $msg]));
        return $res->withStatus($code)
                   ->withHeader('Content-Type', 'application/json');
    }
}
