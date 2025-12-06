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
    vim \
    php-sqlite3 \
    php-mysql \
    sqlite3 \
    apt-transport-https \
    ca-certificates \
    gnupg


# Install gcloud cli
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

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
