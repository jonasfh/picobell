<?php
declare(strict_types=1);

use App\Application\Settings\EnvLoader;

require_once __DIR__ . '/../vendor/autoload.php';

EnvLoader::load(__DIR__ . '/.env');

return [
    'type'     => $_ENV['DB_TYPE'],
    'database' => $_ENV['DB_DATABASE'],
    'host'     => $_ENV['DB_HOST'] ?? null,
    'username' => $_ENV['DB_USER'] ?? null,
    'password' => $_ENV['DB_PASS'] ?? null,
    'table_prefix' => $_ENV['APP_ENV'] == 'prod' ? '' : $_ENV['APP_ENV'] . '_',
];
