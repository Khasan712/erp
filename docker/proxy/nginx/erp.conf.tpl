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
