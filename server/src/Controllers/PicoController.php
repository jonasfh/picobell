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

    // === GET /pico/list_py_files ===
    public function listFiles(Request $req, Response $res): Response
    {
        $firmwareDir = __DIR__ . '/../../firmware/latest';
        if (!is_dir($firmwareDir)) {
             return $this->json($res, [], 200);
        }

        $files = [];
        $iterator = new \DirectoryIterator($firmwareDir);
        foreach ($iterator as $fileinfo) {
            if ($fileinfo->isFile() && $fileinfo->getExtension() === 'py') {
                 // Return relative path. Client will prepend BASE_URL from its config.
                 $downloadUrl = '/pico/get_file?file=' . $fileinfo->getFilename();

                 $files[] = [
                     'name' => $fileinfo->getFilename(),
                     'url' => $downloadUrl
                 ];
            }
        }

        return $this->json($res, $files);
    }

    // === GET /pico/get_file ===
    public function getFile(Request $req, Response $res): Response
    {
        $queryParams = $req->getQueryParams();
        $filename = $queryParams['file'] ?? '';

        // Security: Prevent directory traversal
        if (empty($filename) || !preg_match('/^[a-zA-Z0-9_\-\.]+$/', $filename)) {
            return $res->withStatus(400, 'Invalid filename');
        }

        $filePath = __DIR__ . '/../../firmware/latest/' . $filename;

        if (!file_exists($filePath)) {
            return $res->withStatus(404, 'File not found');
        }

        $content = file_get_contents($filePath);
        $res->getBody()->write($content);
        return $res->withHeader('Content-Type', 'text/plain'); // .py files as text
    }

    // === Helper ===
    private function json(Response $res, array $data, int $status = 200): Response
    {
        $res->getBody()->write(json_encode($data, JSON_UNESCAPED_UNICODE));
        return $res->withStatus($status)
                   ->withHeader('Content-Type', 'application/json');
    }
}
