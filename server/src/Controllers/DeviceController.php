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
        $name = $data['device_name'] ?? null;
        $token = $data['device_token'] ?? null;

        if (!$name || !$token) {
            $res->getBody()->write(json_encode([
                'error' => 'Missing device_name or device_token'
            ]));
            return $res->withStatus(400)
                ->withHeader('Content-Type', 'application/json');
        }

        $this->db->insert("devices", [
            "user_id" => $user['id'],
            "name" => $name,
            "token" => $token,
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);

        $res->getBody()->write(json_encode([
            'message' => 'Device registered',
            'id' => $this->db->id()
        ]));
        return $res->withHeader('Content-Type', 'application/json');
    }
}
