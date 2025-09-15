FROM ubuntu:24.04

# Unngå interaktive spørsmål
ENV DEBIAN_FRONTEND=noninteractive

# Installer PHP, Composer og andre verktøy
RUN apt-get update && apt-get install -y \
    php-cli \
    php-fpm \
    php-mbstring \
    php-xml \
    php-curl \
    unzip \
    git \
    curl \
    nano \
    php-sqlite3 \
    php-mysql \
    && rm -rf /var/lib/apt/lists/*

# Installer Composer
RUN curl -sS https://getcomposer.org/installer | php -- \
    --install-dir=/usr/local/bin --filename=composer

# Etter at composer er installert
COPY . /workspace/
RUN composer update --no-interaction || true
RUN cd /workspace/server && composer install --no-interaction --prefer-dist \
    --optimize-autoloader || true
RUN rm -rf /var/www && ln -s /workspace/server /var/www

WORKDIR /workspace
