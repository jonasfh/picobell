<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use App\Services\FcmService;
use Slim\App;
use Medoo\Medoo;
use App\Controllers\AuthController;

return function (App $app, Medoo $db) {


    $auth = new AuthController($db);

    // === AUTH ===
    $app->post('/auth/register', [$auth, 'register']);
    $app->post('/auth/login', [$auth, 'login']);
    $app->get('/auth/profile', [$auth, 'profile'])
        ->add([$auth, 'authMiddleware']);

    // USERS
    $app->get('/db/users', function (Request $req, Response $res) use ($db) {
        $users = $db->select("users", "*");
        $res->getBody()->write(json_encode($users));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->get('/db/users/{id}', function (Request $req, Response $res, $args) use ($db) {
        $user = $db->get("users", "*", ["id" => $args['id']]);
        $res->getBody()->write(json_encode($user));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/db/users', function (Request $req, Response $res) use ($db) {
        $data = $req->getParsedBody();
        $db->insert("users", [
            "email" => $data['email'],
            "password_hash" => password_hash($data['password'], PASSWORD_BCRYPT),
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $db->id()]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->put('/db/users/{id}', function (Request $req, Response $res, $args) use ($db) {
        $data = $req->getParsedBody();
        $db->update("users", [
            "email" => $data['email'] ?? null,
            "modified_at" => date("Y-m-d H:i:s")
        ], ["id" => $args['id']]);
        $res->getBody()->write(json_encode(["updated" => true]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->delete('/db/users/{id}', function (Request $req, Response $res, $args) use ($db) {
        $db->delete("users", ["id" => $args['id']]);
        $res->getBody()->write(json_encode(["deleted" => true]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    // APARTMENTS
    $app->get('/db/apartments', function (Request $req, Response $res) use ($db) {
        $res->getBody()->write(json_encode($db->select("apartments", "*")));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/db/apartments', function (Request $req, Response $res) use ($db) {
        $data = $req->getParsedBody();
        $db->insert("apartments", [
            "address" => $data['address'],
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $db->id()]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    // DEVICES
    $app->get('/db/devices', function (Request $req, Response $res) use ($db) {
        $res->getBody()->write(json_encode($db->select("devices", "*")));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/db/devices', function (Request $req, Response $res) use ($db) {
        $data = $req->getParsedBody();
        $db->insert("devices", [
            "user_id" => $data['user_id'],
            "apartment_id" => $data['apartment_id'],
            "token" => $data['token'],
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $db->id()]));
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
