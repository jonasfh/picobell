<?php

namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;

class ApartmentController {
    private $db;
    public function __construct(Medoo $db) { $this->db = $db; }

    public function list(Request $req, Response $res): Response {
        $apartments = $this->db->select("apartments", [
            "id",
            "address",
            "pico_serial",
            "created_at",
            "modified_at"
        ]);

        $res->getBody()->write(json_encode($apartments));
        return $res->withHeader('Content-Type', 'application/json');
    }

    public function create(Request $req, Response $res): Response {
        $data = $req->getParsedBody();

        $apiKey = bin2hex(random_bytes(32));

        $this->db->insert("apartments", [
            "address" => $data['address'],
            "pico_serial" => $data['pico_serial'],
            "api_key" => $apiKey,
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);

        $res->getBody()->write(json_encode([
            "id" => $this->db->id(),
            "api_key" => $apiKey
        ]));

        return $res->withHeader('Content-Type', 'application/json');
    }
}
