<?php

namespace App\Controllers;

use Medoo\Medoo;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Google\Client as Google_Client;

class AuthController
{
    private Medoo $db;
    private string $jwtSecret;

    public function __construct(Medoo $db)
    {
        $this->db = $db;
        $this->jwtSecret = getenv('JWT_SECRET');
    }

    public function register(Request $req, Response $res): Response
    {
        $data = $req->getParsedBody();
        $email = $data['email'] ?? null;
        $password = $data['password'] ?? null;
        if (!$email || !$password) {
            return $this->json($res, ['error' => 'Missing fields'], 400);
        }

        $this->db->insert("users", [
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

        $jwt = $this->createJwtForUser($user);
        return $this->json($res, ["token" => $jwt]);
    }
    // Login with Google OAuth
    public function google(Request $req, Response $res) {
        $data = $req->getParsedBody();
        $idToken = $data['id_token'] ?? null;

        if (!$idToken) {
            return $this->json($res, ["error" => "Missing id_token"], 400);
        }

        $client = new \Google_Client(['client_id' => $_ENV['GOOGLE_CLIENT_ID']]);
        $payload = $client->verifyIdToken($idToken);

        if (!$payload) {
            return $this->json($res, ["error" => "Invalid Google token"], 401);
        }

        $email = $payload['email'];

        // Hent eller opprett bruker
        $user = $this->db->get("users", "*", ["email" => $email]);
        if (!$user) {
            $this->db->insert("users", [
                "email" => $email,
                "role" => "user",
                "created_at" => date("Y-m-d H:i:s"),
                "modified_at" => date("Y-m-d H:i:s")
            ]);

            $userId = $this->db->id();   // <- dette gir deg faktisk ID-en
            $user = $this->db->get("users", "*", ["id" => $userId]);
        }

        $token = $this->createJwtForUser($user);
        return $this->json($res, ["token" => $token]);
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

    private function createJwtForUser($user) {
        $now = time();
        $exp = $now + 3600; // Token gyldig i 1 time

        $payload = [
            'iat' => $now,
            'exp' => $exp,
            'sub' => $user['id'],
            'email' => $user['email'],
            'role' => $user['role'],
        ];
        error_log("Creating JWT for user ID {$user['id']} with payload: " . json_encode($payload));
        error_log("Using JWT secret: " . $this->jwtSecret);
        return \Firebase\JWT\JWT::encode(
            $payload,
            $this->jwtSecret,
            'HS256'
        );
    }

}
