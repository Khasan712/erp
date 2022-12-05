upstream django {
    server app:8000;
}

server {
    listen: 80;
    server_name: backend.jmb-inventory-system.com;

    location /.well-known/acme-challange/ {
        root /var/www;
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

    ssl_session_cache shared:le_nginx_SSL:10m;
    ssl_session_timeout 1440m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";


    ssl_dhparam /var/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always

    location /static/ {
        root /var/static/;
    }

    location / {
        proxy_pass http://django;
        client_max_body_size 10M;
    }
}

