<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use App\Service\FcmService;

class DoorbellController {
    public function ring(Request $req, Response $res): Response {
        $body = $req->getParsedBody();
        $token = $body['token'] ?? null;

        if (!$token) {
            $res = $res->withStatus(400);
            $res->getBody()->write(json_encode(['error' => 'Missing device token']));
            return $res->withHeader('Content-Type', 'application/json');
        }

        $fcm = new FcmService(
            getenv('FIREBASE_PROJECT_ID'),
            __DIR__ . '/../../' . getenv('SERVICE_ACCOUNT_PATH')
        );

        try {
            $result = $fcm->sendNotification(
                $token,
                'Ring på døra!',
                'Noen står utenfor og ringer på 🚪🔔'
            );
            $res->getBody()->write(json_encode($result, JSON_UNESCAPED_UNICODE));
        } catch (\Throwable $e) {
            $res = $res->withStatus(500);
            $res->getBody()->write(json_encode([
                'error' => $e->getMessage()
            ], JSON_UNESCAPED_UNICODE));
        }
        return $res->withHeader('Content-Type', 'application/json');
    }

    public function open(Request $req, Response $res): Response {
        $res->getBody()->write(json_encode(['message' => 'Open command sent']));
        return $res->withHeader('Content-Type', 'application/json');
    }
}
