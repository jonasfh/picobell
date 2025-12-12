<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;

class ProfileController {
    private $db;
    public function __construct(Medoo $db) { $this->db = $db; }

    public function getProfile(Request $req, Response $res): Response {
        $userAttr = $req->getAttribute('user');
        $profile = $this->db->get("users", [
            "id", "email", "role", "created_at", "modified_at"
        ], ["email" => $userAttr['email']]);

        try {
            $apartments = $this->db->select("apartments",
                ["[><]user_apartment" => [
                    "apartments.id" => "apartment_id",
                    "AND" => ["user_id" => $profile['id']]
                ]],
                ["apartments.id", "apartments.address", "user_apartment.role",
                 "apartments.created_at", "apartments.modified_at"]
            );
        } catch (\Exception $e) {
            error_log("Feil ved henting av leiligheter: ".$e->getMessage());
            $apartments = [];
        }
        $profile['apartments'] = $apartments;

        $devices = $this->db->select("devices",
            ["id","name","created_at","modified_at"],
            ["user_id" => $profile['id']]
        );
        $profile['devices'] = $devices;

        $res->getBody()->write(json_encode($profile));
        return $res->withHeader('Content-Type', 'application/json');
    }
}
