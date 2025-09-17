<?php

declare(strict_types=1);

use App\Application\Settings\EnvLoader;
use Slim\Factory\AppFactory;
use Medoo\Medoo;

require __DIR__ . '/../vendor/autoload.php';

EnvLoader::load(__DIR__ . '/../config/.env');


$database = new Medoo([
    'type' => $_ENV['DB_TYPE'] ?? 'sqlite',
    'database' => $_ENV['DB_DATABASE'] ?? __DIR__ . '/../db/dev.sqlite',
    'host' => $_ENV['DB_HOST'] ?? null,
    'username' => $_ENV['DB_USER'] ?? null,
    'password' => $_ENV['DB_PASS'] ?? null,
    'port' => $_ENV['DB_PORT'] ?? null,
    'charset' => 'utf8mb4',
]);

// === Opprett Slim-app ===
$app = AppFactory::create();
$app->addRoutingMiddleware();

// Feilmeldinger styres av APP_ENV
$displayErrorDetails = ($_ENV['APP_ENV'] ?? 'prod') === 'dev';
$app->addErrorMiddleware($displayErrorDetails, true, true);

// === Eksempel: bruk av DB i en route ===
$app->get('/health', function ($request, $response) use ($database) {
    $dbOk = true;
    try {
        $database->query('SELECT 1');
    } catch (\Throwable $e) {
        $dbOk = false;
    }

    $payload = [
        'status' => 'ok',
        'env' => $_ENV['APP_ENV'] ?? 'unknown',
        'db' => $dbOk ? 'connected' : 'error',
    ];

    $response->getBody()->write(json_encode($payload));
    return $response->withHeader('Content-Type', 'application/json');
});

// === Start app ===
$app->run();
