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
    $app->group('/profile', function ($group) use ($profile, $devices, $apartments) {
        // Henter brukers egen profil
        $group->get('', [$profile, 'getProfile']);

        // Devices under /profile/devices
        $group->group('/devices', function ($sub) use ($devices) {
            $sub->get('', [$devices, 'list']);
            $sub->post('/register', [$devices, 'register']);
        });

        // Apartments under /profile/apartments
        $group->group('/apartments', function ($sub) use ($apartments) {
            $sub->get('', [$apartments, 'list']);
            $sub->post('', [$apartments, 'create']);
        });
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
        $group->post('/status', [$doorbell, 'status']);
    })->add([$auth, 'authMiddleware']);
};
