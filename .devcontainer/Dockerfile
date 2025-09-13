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

# Use google name servers to avoid DNS issues
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
RUN echo "nameserver 8.8.4.4" >> /etc/resolv.conf

WORKDIR /workspace
