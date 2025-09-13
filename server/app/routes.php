<?php

declare(strict_types=1);

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\App;
use App\Service\FcmService;


return function (App $app) {
    $app->options('/{routes:.*}', function (
        Request $request,
        Response $response
    ) {
        // CORS Pre-Flight OPTIONS Request Handler
        return $response;
    });

    $app->get('/', function (Request $request, Response $response) {
        $response->getBody()->write('Hello Ylva!');
        return $response;
    });

    // Helse-sjekk
    $app->get('/health', function (Request $req, Response $res) {
        $res->getBody()->write(json_encode(['status' => 'ok']));
        return $res->withHeader('Content-Type', 'application/json');
    });

    // Pico melder fra når noen ringer på
    $app->post('/doorbell/ring', function (Request $req, Response $res) {
        $body = $req->getParsedBody();
        $token = $body['token'] ?? null;

        if (!$token) {
            $res = $res->withStatus(400);
            $res->getBody()->write(json_encode([
                'error' => 'Missing device token'
            ]));
            return $res->withHeader('Content-Type', 'application/json');
        }

        $fcm = new FcmService(
            getenv('FIREBASE_PROJECT_ID'),
            __DIR__ . '/../' . getenv('SERVICE_ACCOUNT_PATH')
        );

        try {
            $result = $fcm->sendNotification(
                $token,
                'Ring på døra!',
                'Noen står utenfor og ringer på 🚪🔔'
            );
            $res->getBody()->write(
                json_encode($result, JSON_UNESCAPED_UNICODE)
            );
        } catch (\Throwable $e) {
            $res = $res->withStatus(500);
            $res->getBody()->write(json_encode([
                'error' => $e->getMessage()
            ], JSON_UNESCAPED_UNICODE));
        }

        return $res->withHeader('Content-Type', 'application/json');
    });

    // Mobil-app trykker åpne
    $app->post('/doorbell/open', function (Request $req, Response $res) {
        // TODO: sende melding til Pico (MQTT, HTTP eller WebSocket)
        $res->getBody()->write(json_encode(['message' => 'Open command sent']));
        return $res->withHeader('Content-Type', 'application/json');
    });
};
