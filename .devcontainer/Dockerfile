# .devcontainer/Dockerfile
FROM ubuntu:24.04

# Unngå interaktive spørsmål
ENV DEBIAN_FRONTEND=noninteractive

# Installer PHP, Composer og andre verktøy
RUN apt-get update && apt-get install -y \
    php-cli \
    php-fpm \
    php-mbstring \
    php-xml \
    unzip \
    git \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Installer Composer
RUN curl -sS https://getcomposer.org/installer | php -- \
    --install-dir=/usr/local/bin --filename=composer

WORKDIR /var/www

