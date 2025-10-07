<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;

class DeviceController {
    private $db;
    public function __construct(Medoo $db) { $this->db = $db; }

    public function list(Request $req, Response $res): Response {
        $devices = $this->db->select("devices", "*");
        $res->getBody()->write(json_encode($devices));
        return $res->withHeader('Content-Type', 'application/json');
    }

    public function register(Request $req, Response $res): Response {
        $userAttr = $req->getAttribute('user');
        $user = $this->db->get("users", "*", ["email" => $userAttr['email']]);
        $data = $req->getParsedBody();
        $token = $data['device_token'] ?? null;
        $name  = $data['device_name'] ?? null;

        if (!$token) {
            $res->getBody()->write(json_encode([
                'error' => 'Missing device_token'
            ]));
            return $res->withStatus(400)
                       ->withHeader('Content-Type', 'application/json');
        }

        $now = date("Y-m-d H:i:s");

        // Sjekk om device med samme token allerede finnes for brukeren
        $existing = $this->db->get("devices", "*", [
            "user_id" => $user['id'],
            "token" => $token
        ]);

        if ($existing) {
            $this->db->update("devices", [
                "name" => $name ?? $existing['name'],
                "last_seen" => $now,
                "modified_at" => $now
            ], ["id" => $existing['id']]);

            $deviceId = $existing['id'];
            $message = 'Device updated';
        } else {
            $this->db->insert("devices", [
                "user_id" => $user['id'],
                "name" => $name,
                "token" => $token,
                "last_seen" => $now,
                "created_at" => $now,
                "modified_at" => $now
            ]);

            $deviceId = $this->db->id();
            $message = 'Device registered';
        }

        $res->getBody()->write(json_encode([
            'message' => $message,
            'id' => $deviceId
        ]));
        return $res->withHeader('Content-Type', 'application/json');
    }
}
