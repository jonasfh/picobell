<?php
declare(strict_types=1);

$db = require __DIR__ . '/database.php';

return [
    'paths' => [
        'migrations' => __DIR__ . '/../db/migrations',
        'seeds'      => __DIR__ . '/../db/seeds',
    ],
    'environments' => [
        'default_migration_table' => 'phinxlog',
        'default_environment'     => 'dev',

        'dev' => [
            'adapter' => $db['type'],
            'name'    => $db['database'],
            'host'    => $db['host'],
            'user'    => $db['username'],
            'pass'    => $db['password'],
            'suffix' => '',
        ],
    ],
    'version_order' => 'creation',
];
