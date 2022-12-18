FROM nginx:latest
COPY ./conf/default.conf /etc/nginx/conf.d/
COPY ./conf/proxy_params /etc/nginx/proxy_params


COPY ./certbot/fullchain.pem /etc/letsencrypt/live/backend.jmb-inventory-system.com/fullchain.pem
COPY ./certbot/privkey.pem /etc/letsencrypt/live/backend.jmb-inventory-system.com/privkey.pem
COPY ./certbot/options-ssl-nginx.conf /etc/letsencrypt/options-ssl-nginx.conf
COPY ./certbot/ssl-dhparams.pem /etc/letsencrypt/ssl-dhparams.pem


RUN mkdir -p /home/app/staticfiles
RUN mkdir -p /home/app/media