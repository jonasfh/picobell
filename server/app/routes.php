<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\App;
use Medoo\Medoo;

return function (App $app, Medoo $db) {

    // USERS
    $app->get('/users', function (Request $req, Response $res) use ($db) {
        $users = $db->select("users", "*");
        $res->getBody()->write(json_encode($users));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->get('/users/{id}', function (Request $req, Response $res, $args) use ($db) {
        $user = $db->get("users", "*", ["id" => $args['id']]);
        $res->getBody()->write(json_encode($user));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/users', function (Request $req, Response $res) use ($db) {
        $data = $req->getParsedBody();
        $db->insert("users", [
            "email" => $data['email'],
            "password_hash" => password_hash($data['password'], PASSWORD_BCRYPT),
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $db->id()]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->put('/users/{id}', function (Request $req, Response $res, $args) use ($db) {
        $data = $req->getParsedBody();
        $db->update("users", [
            "email" => $data['email'] ?? null,
            "modified_at" => date("Y-m-d H:i:s")
        ], ["id" => $args['id']]);
        $res->getBody()->write(json_encode(["updated" => true]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->delete('/users/{id}', function (Request $req, Response $res, $args) use ($db) {
        $db->delete("users", ["id" => $args['id']]);
        $res->getBody()->write(json_encode(["deleted" => true]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    // APARTMENTS
    $app->get('/apartments', function (Request $req, Response $res) use ($db) {
        $res->getBody()->write(json_encode($db->select("apartments", "*")));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/apartments', function (Request $req, Response $res) use ($db) {
        $data = $req->getParsedBody();
        $db->insert("apartments", [
            "address" => $data['address'],
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $db->id()]));
        return $res->withHeader('Content-Type', 'application/json');
    });

    // DEVICES
    $app->get('/devices', function (Request $req, Response $res) use ($db) {
        $res->getBody()->write(json_encode($db->select("devices", "*")));
        return $res->withHeader('Content-Type', 'application/json');
    });

    $app->post('/devices', function (Request $req, Response $res) use ($db) {
        $data = $req->getParsedBody();
        $db->insert("devices", [
            "user_id" => $data['user_id'],
            "apartment_id" => $data['apartment_id'],
            "token" => $data['token'],
            "created_at" => date("Y-m-d H:i:s"),
            "modified_at" => date("Y-m-d H:i:s")
        ]);
        $res->getBody()->write(json_encode(["id" => $db->id()]));
        return $res->withHeader('Content-Type', 'application/json');
    });
};
