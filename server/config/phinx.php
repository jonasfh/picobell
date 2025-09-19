<?php
declare(strict_types=1);

$db = require __DIR__ . '/database.php';
$credentials = [
    'adapter' => $db['type'],
    'name'    => $db['database'],
    'host'    => $db['host'],
    'user'    => $db['username'],
    'pass'    => $db['password'],
    'table_prefix'  => $db['table_prefix'],
    'suffix'  => '',
    'migration_table' => $db['table_prefix'] . 'phinxlog',
];
return [
    'paths' => [
        'migrations' => __DIR__ . '/../db/migrations',
        'seeds'      => __DIR__ . '/../db/seeds',
    ],
    'environments' => [
        'default_migration_table' => 'phinxlog',
        'default_environment'     => 'dev',
        'dev' => $credentials,
        'prod' => $credentials,
    ],
    'version_order' => 'creation',
];
