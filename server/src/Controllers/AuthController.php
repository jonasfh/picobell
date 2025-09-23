<?php

namespace App\Controllers;

use Medoo\Medoo;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class AuthController
{
    private Medoo $db;
    private string $jwtSecret;

    public function __construct(Medoo $db)
    {
        $this->db = $db;
        $this->jwtSecret = $_ENV['JWT_SECRET'] ?? 'dev-secret-key';
    }

    public function register(Request $req, Response $res): Response
    {
        $data = $req->getParsedBody();
        $email = $data['email'] ?? null;
        $password = $data['password'] ?? null;
        $username = $data['username'] ?? null;

        if (!$email || !$password || !$username) {
            return $this->json($res, ['error' => 'Missing fields'], 400);
        }

        $this->db->insert("users", [
            "username" => $username,
            "email" => $email,
            "password_hash" => password_hash($password, PASSWORD_BCRYPT),
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);

        return $this->json($res, ['id' => $this->db->id()]);
    }

    public function login(Request $req, Response $res): Response
    {
        $data = $req->getParsedBody();
        $email = $data['email'] ?? null;
        $password = $data['password'] ?? null;

        $user = $this->db->get("users", "*", ["email" => $email]);
        if (!$user || !password_verify($password, $user['password_hash'])) {
            return $this->json($res, ['error' => 'Invalid credentials'], 401);
        }

        $payload = [
            "sub" => $user['id'],
            "email" => $user['email'],
            "iat" => time(),
            "exp" => time() + 3600 // 1 time
        ];

        $jwt = JWT::encode($payload, $this->jwtSecret, 'HS256');

        return $this->json($res, ["token" => $jwt]);
    }

    public function profile(Request $req, Response $res): Response
    {
        $user = $req->getAttribute("user");
        return $this->json($res, $user);
    }

    private function json(Response $res, $data, int $status = 200): Response
    {
        $res->getBody()->write(json_encode($data));
        return $res
            ->withStatus($status)
            ->withHeader('Content-Type', 'application/json');
    }

    // Middleware for å sjekke token
    public function authMiddleware(Request $req, $handler): Response
    {
        $authHeader = $req->getHeaderLine("Authorization");
        if (!$authHeader || !str_starts_with($authHeader, "Bearer ")) {
            $response = new \Slim\Psr7\Response();
            $response->getBody()->write(json_encode(["error" => "Missing token"]));
            return $response->withStatus(401)
                ->withHeader("Content-Type", "application/json");
        }

        $jwt = substr($authHeader, 7);
        try {
            $decoded = JWT::decode($jwt, new Key($this->jwtSecret, 'HS256'));
            $req = $req->withAttribute("user", (array) $decoded);
            return $handler->handle($req);
        } catch (\Throwable $e) {
            $response = new \Slim\Psr7\Response();
            $response->getBody()->write(json_encode(["error" => "Invalid token"]));
            return $response->withStatus(401)
                ->withHeader("Content-Type", "application/json");
        }
    }
}
