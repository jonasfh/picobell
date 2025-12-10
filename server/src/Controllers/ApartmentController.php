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
        // fail if pico_serial is missing
        if (!isset($data['pico_serial']) || !isset($data['address'])) {
            $res->getBody()->write(json_encode([
                "error" => "Missing pico_serial or address"
            ]));
            return $res->withStatus(400)->withHeader('Content-Type', 'application/json');
        }

        // Fail if pico_serial is already in use
        $existing = $this->db->get("apartments", "*", [
            "pico_serial" => $data['pico_serial']
        ]);
        if ($existing) {
            $res->getBody()->write(json_encode([
                "error" => "Apartment with this pico_serial already exists"
            ]));
            return $res->withStatus(409)->withHeader('Content-Type', 'application/json');
        }
        $api_key = bin2hex(random_bytes(32));
        // Create new apartment
        $this->db->insert("apartments", [
            "address" => $data['address'],
            "pico_serial" => $data['pico_serial'],
            "api_key" => $api_key,
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);

        // Also link the apartment to the user creating it
        $user = $req->getAttribute("user");
        $this->db->insert("user_apartment", [
            "user_id" => $user['id'],
            "apartment_id" => $this->db->id(),
            "role" => "owner",
        ]);

        $res->getBody()->write(json_encode([
            "id" => $this->db->id(),
            "api_key" => $api_key
        ]));

        return $res->withHeader('Content-Type', 'application/json');
    }

    public function rename(Request $req, Response $res, array $args): Response {
        $apartmentId = $args['id'];
        $data = $req->getParsedBody();
        if (!isset($data['address'])) {
            $res->getBody()->write(json_encode([
                "error" => "Missing address"
            ]));
            return $res->withStatus(400)->withHeader('Content-Type', 'application/json');
        }
        // check that the user has access to this apartment, and is owner
        $user = $req->getAttribute("user");
        $access = $this->db->get("user_apartment", "*", [
            "user_id" => $user['id'],
            "apartment_id" => $apartmentId,
            "role" => "owner"
        ]);
        if (!$access) {
            $res->getBody()->write(json_encode([
                "error" => "Must be owner to rename apartment"
            ]));
            return $res->withStatus(403)->withHeader('Content-Type', 'application/json');
        }

        // Update apartment address
        $this->db->update("apartments", [
            "address" => $data['address'],
            "modified_at" => date("Y-m-d H:i:s")
        ], [
            "id" => $apartmentId
        ]);

        $res->getBody()->write(json_encode([
            "message" => "Apartment renamed successfully"
        ]));

        return $res->withHeader('Content-Type', 'application/json');
    }
}
