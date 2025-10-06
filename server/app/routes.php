<?php

use Slim\App;
use Medoo\Medoo;
use App\Controllers\AuthController;
use App\Controllers\ProfileController;
use App\Controllers\DeviceController;
use App\Controllers\ApartmentController;
use App\Controllers\AdminController;
use App\Controllers\DoorbellController;

return function (App $app, Medoo $db) {
    $auth = new AuthController($db);
    $profile = new ProfileController($db);
    $devices = new DeviceController($db);
    $apartments = new ApartmentController($db);
    $admin = new AdminController($db);
    $doorbell = new DoorbellController($db);

    // === AUTH ===
    $app->group('/auth', function ($group) use ($auth) {
        $group->post('/register', [$auth, 'register']);
        $group->post('/login', [$auth, 'login']);
        $group->post('/google', [$auth, 'google']);
    });

    // === PROFILE ===
    $app->group('/profile', function ($group) use ($profile) {
        $group->get('', [$profile, 'getProfile']);
    })->add([$auth, 'authMiddleware']);

    // === DEVICES ===
    $app->group('/devices', function ($group) use ($devices) {
        $group->get('', [$devices, 'list']);
        $group->post('/register', [$devices, 'register']);
    })->add([$auth, 'authMiddleware']);

    // === APARTMENTS ===
    $app->group('/apartments', function ($group) use ($apartments) {
        $group->get('', [$apartments, 'list']);
        $group->post('', [$apartments, 'create']);
    })->add([$auth, 'authMiddleware']);

    // === ADMIN ===
    $app->group('/admin', function ($group) use ($admin) {
        $group->get('/users', [$admin, 'listUsers']);
        $group->get('/users/{id}', [$admin, 'getUser']);
        $group->post('/users', [$admin, 'createUser']);
    })->add([$auth, 'authMiddleware']);

    // === DOORBELL ===
    $app->group('/doorbell', function ($group) use ($doorbell) {
        $group->post('/ring', [$doorbell, 'ring']);
        $group->post('/open', [$doorbell, 'open']);
    });
};
