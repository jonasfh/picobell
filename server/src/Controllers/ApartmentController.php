<?php

namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;

class ApartmentController {
    private Medoo $db;
    public function __construct(Medoo $db) { $this->db = $db; }

    public function list(Request $req, Response $res): Response {
        # use the user-object in the request to filter only apartments the user
        # has access to. Users are connected to apartments via the user_apartment table.
        $user = $req->getAttribute("user");
        $apartments = $this->db->select(
            "apartments (a)",
            [
                '[>]user_apartment' =>['a.id'=>'apartment_id']
            ], [
            "a.id",
            "address",
            "pico_serial",
            "a.created_at",
            "a.modified_at"
        ], [
            "user_id" => $user['id']
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
