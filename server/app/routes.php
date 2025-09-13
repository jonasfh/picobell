<?php

declare(strict_types=1);

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\App;

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
        // TODO: trigge FCM push-varsler til mobil
        $res->getBody()->write(json_encode(['message' => 'Ring event received']));
        return $res->withHeader('Content-Type', 'application/json');
    });

    // Mobil-app trykker åpne
    $app->post('/doorbell/open', function (Request $req, Response $res) {
        // TODO: sende melding til Pico (MQTT, HTTP eller WebSocket)
        $res->getBody()->write(json_encode(['message' => 'Open command sent']));
        return $res->withHeader('Content-Type', 'application/json');
    });
};
