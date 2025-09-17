<?php
declare(strict_types=1);

use App\Application\Settings\EnvLoader;

require_once __DIR__ . '/../vendor/autoload.php';

EnvLoader::load(__DIR__ . '/../config/.env');

return
[
    'paths' => [
        'migrations' => __DIR__ . '/../db/migrations',
        'seeds'      => __DIR__ . '/../db/seeds',
    ],
    'environments' => [
        'default_migration_table' => 'phinxlog',
        'default_environment'     => 'development',

        'development' => [
            'adapter' => 'sqlite',
            'name'    => '/tmp/db.sqlite',
            'suffix'  => '',
        ],
    ],
    'version_order' => 'creation',
];
