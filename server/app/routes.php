<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use App\Service\FcmService;
use Slim\App;
use Medoo\Medoo;
use App\Controllers\AuthController;

return function (App $app, Medoo $db) {
    $auth = new AuthController($db);

    // === PUBLIC (ingen auth) ===
    $app->group('/auth', function ($group) use ($auth) {
        $group->post('/register', [$auth, 'register']);
        $group->post('/login', [$auth, 'login']);
        $group->post('/google', [$auth, 'google']);
    });

    // === PROFILE (krever auth) ===
    $app->group('/profile', function ($group) use ($db) {
        $group->get('', function (Request $req, Response $res) use ($db) {
            $user = $req->getAttribute('user');

            // Hent bruker
            $profile = $db->get("users", [
                "id", "email", "role", "created_at", "modified_at"
            ], ["email" => $user['email']]);

            // // Hent apartments via koblingstabellen
            try {
                $apartments = $db->select("apartments", 
                    [
                        "[><]user_apartment" => [
                            "apartments.id" => "apartment_id",
                            "AND" => [
                                "user_id" => $profile['id']
                            ]
                        ]
                    ],
                    [
                        "apartments.id",
                        "apartments.address",
                        "apartments.created_at",
                        "apartments.modified_at"
                    ]
                );
            } catch (Exception $e) {
                // Ignorer feil hvis det ikke fungerer
                error_log("Feil ved henting av leiligheter: " . $e->getMessage());
                $apartments = [];
            }
            $profile['apartments'] = $apartments;

            $devices = $db->select("devices", [
                "id", "name", "created_at", "modified_at"
            ], ["user_id" => $profile['id']]);
            $profile['devices'] = $devices;
            $res->getBody()->write(json_encode($profile));
            return $res->withHeader('Content-Type', 'application/json');
        });

        // eksempel på ressurs-endepunkter
        $group->get('/devices', function (Request $req, Response $res) use ($db) {
            $res->getBody()->write(json_encode($db->select("devices", "*")));
            return $res->withHeader('Content-Type', 'application/json');
        });

        $group->post('/devices', function (Request $req, Response $res) use ($db) {
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

        $group->get('/apartments', function (Request $req, Response $res) use ($db) {
            $res->getBody()->write(json_encode($db->select("apartments", "*")));
            return $res->withHeader('Content-Type', 'application/json');
        });

        $group->post('/apartments', function (Request $req, Response $res) use ($db) {
            $data = $req->getParsedBody();
            $db->insert("apartments", [
                "address" => $data['address'],
                "created_at" => date("Y-m-d H:i:s"),
                "modified_at" => date("Y-m-d H:i:s")
            ]);
            $res->getBody()->write(json_encode(["id" => $db->id()]));
            return $res->withHeader('Content-Type', 'application/json');
        });
    })->add([$auth, 'authMiddleware']);

    // === ADMIN (krever auth) ===
    $app->group('/admin', function ($group) use ($db) {
        $group->get('/users', function (Request $req, Response $res) use ($db) {
            $users = $db->select("users", "*");
            $res->getBody()->write(json_encode($users));
            return $res->withHeader('Content-Type', 'application/json');
        });

        $group->get('/users/{id}', function (Request $req, Response $res, $args) use ($db) {
            $user = $db->get("users", "*", ["id" => $args['id']]);
            $res->getBody()->write(json_encode($user));
            return $res->withHeader('Content-Type', 'application/json');
        });

        $group->post('/users', function (Request $req, Response $res) use ($db) {
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
    })->add([$auth, 'authMiddleware']);

    // === DOORBELL (public events fra Pico) ===
    $app->post('/doorbell/ring', function (Request $req, Response $res) {
        $body = $req->getParsedBody();
        $token = $body['token'] ?? null;

        if (!$token) {
            $res = $res->withStatus(400);
            $res->getBody()->write(json_encode(['error' => 'Missing device token']));
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
            $res->getBody()->write(json_encode($result, JSON_UNESCAPED_UNICODE));
        } catch (\Throwable $e) {
            $res = $res->withStatus(500);
            $res->getBody()->write(json_encode([
                'error' => $e->getMessage()
            ], JSON_UNESCAPED_UNICODE));
        }

        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/doorbell/open', function (Request $req, Response $res) {
        $res->getBody()->write(json_encode(['message' => 'Open command sent']));
        return $res->withHeader('Content-Type', 'application/json');
    });
};
