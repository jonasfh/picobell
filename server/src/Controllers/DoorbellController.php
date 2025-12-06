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
        $body = $req->getParsedBody();
        $picoSerial = $body['pico_serial'] ?? null;
        if (!$picoSerial) {
            return $this->jsonError($res, 'Missing pico_serial', 400);
        }

        // Registrer ny doorbell event
        $this->db->insert('doorbell_events', [
            'pico_serial' => $picoSerial,
        ]);

        // Finn apartment knyttet til pico
        $apartment = $this->db->get('apartments', '*', [
            'pico_serial' => $picoSerial,
        ]);
        if (!$apartment) {
            return $this->jsonError($res, 'Unknown pico_serial', 404);
        }

        // Finn brukere og deres aktive devices
        $userIds = $this->db->select('user_apartment', 'user_id', [
            'apartment_id' => $apartment['id'],
        ]);
        $devices = $this->db->select('devices', ['token'], [
            'user_id' => $userIds,
        ]);

        if (!empty($devices)) {

            foreach ($devices as $device) {
                $result = $this->fcm->sendDataMessage(
                    $device['token'],
                    [
                        'apartment_id' => (string) $apartment['id'],
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

    // === POST /doorbell/open ===
    public function open(Request $req, Response $res): Response
    {
        $userAttr = $req->getAttribute('user');
        $userId = $userAttr['id'] ?? null;
        if (!$userId) {
            return $this->jsonError($res, 'Unauthorized', 401);
        }
        $body = $req->getParsedBody();

        $apartmentId = intval($body['apartment_id'] ?? null);
        if (!$apartmentId) {
            return $this->jsonError($res, 'Missing apartment_id', 400);
        }

        // Sjekk om apartment id er knyttet til bruker. tabeller:
        // users, user_apartment, apartments
        $linkedApartment = $this->db->get('user_apartment', '*', [
            'user_id' => $userId,
            'apartment_id' => $apartmentId,
        ]);
        if (!$linkedApartment) {
            return $this->jsonError($res, 'Apartment not linked to user', 403);
        }


        // Finn siste doorbell-event for apartment
        $picoSerial = $this->db->get('apartments', 'pico_serial', [
            'id' => $apartmentId,
        ]);
        if (!$picoSerial) {
            return $this->jsonError($res, 'No pico for apartment', 404);
        }

        $event = $this->db->get('doorbell_events', '*', [
            'pico_serial' => $picoSerial,
            'ORDER' => ['created_at' => 'DESC'],
        ]);
        if (!$event) {
            return $this->jsonError($res, 'No active ring found', 404);
        }

        // Sett open_requested = true
        $this->db->update('doorbell_events', [
            'open_requested' => true,
        ], ['id' => $event['id']]);

        return $this->json($res, [
            'message' => 'Door open requested',
            'event_id' => $event['id'],
        ]);
    }

    // === GET /doorbell/status?pico_serial=XYZ ===
    public function status(Request $req, Response $res): Response
    {
        $params = $req->getQueryParams();
        $picoSerial = $params['pico_serial'] ?? null;

        if (!$picoSerial) {
            return $this->jsonError($res, 'Missing pico_serial', 400);
        }

        // Finn siste event for pico
        $event = $this->db->get('doorbell_events', '*', [
            'pico_serial' => $picoSerial,
            'opened_at' => null,
            'ORDER' => ['created_at' => 'DESC'],
            'LIMIT' => 1,
        ]);

        $open = $event && $event['open_requested'];
        # Update event to reset open_requested after checking
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
