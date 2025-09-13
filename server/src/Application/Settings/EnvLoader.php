<?php

namespace App\Application\Settings;

class EnvLoader
{
    /**
     * Load .env file into getenv(), $_ENV and $_SERVER
     */
    public static function load(string $file): void
    {
        if (!file_exists($file)) {
            throw new \RuntimeException(".env file not found: $file");
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
    }
}
