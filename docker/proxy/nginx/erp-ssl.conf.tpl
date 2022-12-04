upstream django {
    server app:8000;
}

server {
    listen: 80;
    server_name: backend.jmb-inventory-system.com;

    location /.well-known/acme-challange/ {
        root /vol/www/;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name: backend.jmb-inventory-system.com;

    ssl_certificate /etc/letsencrypt/live/backend.jmb-inventory-system.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/backend.jmb-inventory-system.com/privkey.pem;

    include /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always

    location /static/ {
        root /vol/static/;
    }

    location / {
        proxy_pass http://django;
        client_max_body_size 10M;
    }
}

