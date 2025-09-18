<?php

namespace App\Application\Settings;

class EnvLoader
{
    private static bool $loaded = false;

    public static function load(string $file): void
    {
        if (self::$loaded) {
            return;
        }
        if (!file_exists($file)) {
            error_log(".env file not found: $file", E_USER_WARNING);
            self::$loaded = true;
            return;
        }

        $lines = file($file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        foreach ($lines as $line) {
            $line = trim($line);
            if ($line === '' || str_starts_with($line, '#')) continue;

            [$key, $value] = explode('=', $line, 2);
            putenv("$key=$value");
            $_ENV[$key] = $value;
            $_SERVER[$key] = $value;
        }

        self::$loaded = true;
    }
}
