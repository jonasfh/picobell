<?php
namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Medoo\Medoo;
use App\Service\FcmService;
use Error;

class PicoController
{
    private Medoo $db;
    private FcmService $fcm;

    public function __construct(Medoo $db)
    {
        $this->db = $db;
    }

    // === GET /pico/fw_version ===
    public function fwVersion(Request $req, Response $res): Response
    {
        return $this->json($res, [
            'fw_version' => FW_VERSION,
        ]);
    }

    // === Helper ===
    private function json(Response $res, array $data, int $status = 200): Response
    {
        $res->getBody()->write(json_encode($data, JSON_UNESCAPED_UNICODE));
        return $res->withStatus($status)
                   ->withHeader('Content-Type', 'application/json');
    }
}
