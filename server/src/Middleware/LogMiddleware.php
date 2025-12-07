<?php
namespace App\Middleware;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;
use Psr\Http\Server\MiddlewareInterface;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

use Medoo\Medoo;

class LogMiddleware implements MiddlewareInterface
{
    private $db;

    public function __construct(Medoo $db)
    {
        $this->db = $db;
    }

    public function process(
        Request $request,
        RequestHandler $handler
    ): Response {
        $ip = $request->getServerParams()['REMOTE_ADDR'] ?? null;
        $body = (string)$request->getBody();
        $jwt = null;
        if (str_starts_with($request->getHeaderLine("Authorization") ?? "", "Bearer ")) {
            $jwt = substr($request->getHeaderLine("Authorization"), 7);
        }

        $email = null;
        if ($jwt) {
            try {
                $decoded = JWT::decode(
                    $jwt,
                    new Key(getenv('JWT_SECRET'), 'HS256')
                );
                $email = $decoded->email ?? null;
            } catch (\Throwable $e) {
                // Invalid token, do nothing, AuthController will handle it
            }
        }

        # unset id_token from $body if present
        $payload = (array)json_decode($body);

        # Make sure to not log sensitive info
        foreach (['id_token', 'password', 'api_key'] as $key) {
            if (isset($payload[$key])) {
                $payload[$key] = '...';
            }
        }

        $payload = json_encode($payload);


        $this->db->insert('api_log', [
            'method' => $request->getMethod(),
            'endpoint' => (string)$request->getUri()->getPath(),
            'ip' => $ip,
            'payload' => $payload,
            'email' => $email ?? null,
        ]);
        return $handler->handle($request);

    }
}
