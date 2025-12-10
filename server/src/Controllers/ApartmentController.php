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

    public function delete(Request $req, Response $res, array $args): Response {
        $apartmentId = $args['id'];
        // check that the user has access to this apartment, and is owner
        $user = $req->getAttribute("user");
        $access = $this->db->get("user_apartment", "*", [
            "user_id" => $user['id'],
            "apartment_id" => $apartmentId,
            "role" => "owner"
        ]);
        if (!$access) {
            $res->getBody()->write(json_encode([
                "error" => "Must be owner to delete apartment"
            ]));
            return $res->withStatus(403)->withHeader('Content-Type', 'application/json');
        }

        // delete all user_apartment links
        $this->db->delete("user_apartment", [
            "apartment_id" => $apartmentId
        ]);

        // Delete apartment
        $this->db->delete("apartments", [
            "id" => $apartmentId
        ]);


        $res->getBody()->write(json_encode([
            "message" => "Apartment deleted successfully"
        ]));

        return $res->withHeader('Content-Type', 'application/json');
    }


    // === POST /profile/apartment/[id]/open ===
    public function openDoor(Request $req, Response $res, array $args): Response
    {
        $userAttr = $req->getAttribute('user');
        $userId = $userAttr['id'] ?? null;
        $apartmentId = intval($args['id'] ?? null);
        if (!$userId) {
            $res->getBody()->write(json_encode([
                "error" => "Unauthorized"
            ]));
            return $res->withStatus(401)->withHeader('Content-Type', 'application/json');
        }

        if (!$apartmentId) {
            $res->getBody()->write(json_encode([
                "error" => "Missing apartment ID"
            ]));
            return $res->withStatus(403)->withHeader('Content-Type', 'application/json');
        }

        // Sjekk om apartment id er knyttet til bruker. tabeller:
        // users, user_apartment, apartments
        $linkedApartment = $this->db->get('user_apartment', '*', [
            'user_id' => $userId,
            'apartment_id' => $apartmentId,
        ]);
        if (!$linkedApartment) {
            $res->getBody()->write(json_encode([
                "error" => "Apartment not linked to user"
            ]));
            return $res->withStatus(403)->withHeader('Content-Type', 'application/json');
        }


        // Finn siste doorbell-event for apartment
        $picoSerial = $this->db->get('apartments', 'pico_serial', [
            'id' => $apartmentId,
        ]);
        if (!$picoSerial) {
            $res->getBody()->write(json_encode([
                "error" => "No pico for apartment"
            ]));
            return $res->withStatus(404)->withHeader('Content-Type', 'application/json');
        }
        error_log("Looking for doorbell event for pico_serial: " . $picoSerial);
        $from = date(
            'Y-m-d H:i:s',
            time() - intval(getenv('EVENT_RING_VALIDITY_SECONDS'))
        );
        error_log("Event after $from");
        $event = $this->db->get('doorbell_events', '*', [
            'pico_serial' => $picoSerial,
            'created_at[>]' => $from,
            'ORDER' => ['created_at' => 'DESC'],
            'LIMIT' => 1,

        ]);
        if (!$event) {
            $res->getBody()->write(json_encode([
                "error" => "No active ring found"
            ]));
            return $res->withStatus(403)->withHeader('Content-Type', 'application/json');
        }

        // Sett open_requested = true
        $this->db->update('doorbell_events', [
            'open_requested' => true,
        ], ['id' => $event['id']]);

        $res->getBody()->write(json_encode([
            'message' => 'Door open requested',
            'event_id' => $event['id'],
        ]));
        return $res->withStatus(200)->withHeader('Content-Type', 'application/json');
    }

}
