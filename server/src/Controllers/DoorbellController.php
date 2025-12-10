<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;
use App\Service\FcmService;
use Error;

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

    // === POST /doorbell/ring ===
    public function ring(Request $req, Response $res): Response
    {
        $apartment = $req->getAttribute('apartment');

        if (!$apartment) {
            return $this->jsonError($res, 'Unauthorized device', 401);
        }

        $picoSerial = $apartment['pico_serial'];

        // Registrer ny doorbell event
        $this->db->insert('doorbell_events', [
            'pico_serial' => $picoSerial,
        ]);

        // Finn brukere og deres aktive devices
        $userIds = $this->db->select('user_apartment', 'user_id', [
            'apartment_id' => $apartment['id'],
        ]);
        $devices = $this->db->select('devices', ['token'], [
            'user_id' => $userIds,
        ]);

        if (!empty($devices)) {
            foreach ($devices as $device) {
                $this->fcm->sendDataMessage(
                    $device['token'],
                    [
                        'apartment_id' => (string)$apartment['id'],
                        'address' => $apartment['address'],
                        'timestamp' => (string) time(),
                    ]
                );
            }
        }

        return $this->json($res, [
            'status' => 'notified',
            'device_count' => count($devices),
        ]);
    }


    // === GET /doorbell/status?pico_serial=XYZ ===
    public function status(Request $req, Response $res): Response
    {
        $apartment = $req->getAttribute('apartment');

        if (!$apartment) {
            return $this->jsonError($res, 'Unauthorized device', 401);
        }

        $picoSerial = $apartment['pico_serial'];

        $from = date(
            'Y-m-d H:i:s',
            time() - intval(getenv('EVENT_RING_VALIDITY_SECONDS'))
        );
        $event = $this->db->get('doorbell_events', '*', [
            'pico_serial' => $picoSerial,
            'opened_at' => null,
            'created_at[>=]' => $from,
            'ORDER' => ['created_at' => 'DESC'],
            'LIMIT' => 1,
        ]);

        $open = $event && $event['open_requested'];

        if ($open) {
            $this->db->update('doorbell_events', [
                'opened_at' => date('Y-m-d H:i:s'),
            ], ['id' => $event['id']]);
        }

        return $this->json($res, ['open' => $open]);
    }

    // === Helper ===
    private function json(Response $res, array $data, int $status = 200): Response
    {
        $res->getBody()->write(json_encode($data, JSON_UNESCAPED_UNICODE));
        return $res->withStatus($status)
                   ->withHeader('Content-Type', 'application/json');
    }

    private function jsonError(Response $res, string $msg, int $status): Response
    {
        return $this->json($res, ['error' => $msg], $status);
    }
}
