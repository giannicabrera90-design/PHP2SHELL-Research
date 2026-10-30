FROM php:8.3-fpm-alpine

# Instalar Nginx y dependencias del sistema esenciales para el laboratorio
RUN apk add --no-cache nginx curl

# Crear directorios de ejecución y logs
RUN mkdir -p /run/nginx /var/www/html

# Copiar configuraciones personalizadas del entorno
COPY php.ini /usr/local/etc/php/php.ini

# Script de prueba básico para recibir las peticiones multipart
RUN echo "<?php echo 'PHP2SHELL Lab Active - Worker ready'; ?>" > /var/www/html/index.php

# Configuración mínima de Nginx para rutear hacia PHP-FPM
RUN echo 'server {' > /etc/nginx/http.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/http.d/default.conf && \
    echo '    root /var/www/html;' >> /etc/nginx/http.d/default.conf && \
    echo '    index index.php;' >> /etc/nginx/http.d/default.conf && \
    echo '    location / {' >> /etc/nginx/http.d/default.conf && \
    echo '        try_files $uri $uri/ =404;' >> /etc/nginx/http.d/default.conf && \
    echo '    }' >> /etc/nginx/http.d/default.conf && \
    echo '    location ~ \.php$ {' >> /etc/nginx/http.d/default.conf && \
    echo '        include fastcgi_params;' >> /etc/nginx/http.d/default.conf && \
    echo '        fastcgi_pass 127.0.0.1:9000;' >> /etc/nginx/http.d/default.conf && \
    echo '        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;' >> /etc/nginx/http.d/default.conf && \
    echo '    }' >> /etc/nginx/http.d/default.conf && \
    echo '}' >> /etc/nginx/http.d/default.conf

EXPOSE 80

# Comando de inicio: Levantar PHP-FPM en segundo plano y Nginx en primer plano
CMD ["sh", "-c", "php-fpm -D && nginx -g 'daemon off;'"]
