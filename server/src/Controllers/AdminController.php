<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;

class AdminController {
    private $db;
    public function __construct(Medoo $db) { $this->db = $db; }

    public function listUsers(Request $req, Response $res): Response {
        $users = $this->db->select("users", "*");
        $res->getBody()->write(json_encode($users));
        return $res->withHeader('Content-Type', 'application/json');
    }

    public function getUser(Request $req, Response $res, array $args): Response {
        $user = $this->db->get("users", "*", ["id" => $args['id']]);
        $res->getBody()->write(json_encode($user));
        return $res->withHeader('Content-Type', 'application/json');
    }

    public function createUser(Request $req, Response $res): Response {
        $data = $req->getParsedBody();
        $this->db->insert("users", [
            "email" => $data['email'],
            "password_hash" => password_hash($data['password'], PASSWORD_BCRYPT),
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $this->db->id()]));
        return $res->withHeader('Content-Type', 'application/json');
    }
}
