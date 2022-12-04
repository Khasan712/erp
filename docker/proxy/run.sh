#!/bin/bash

set -e

echo "Checking for dhparams.pem"
if [ ! -f "/vol/proxy/ssl-dhparams.pem" ]; then
  echo "dhparams.pem does not exist - crating it"
  openssl dhparam -out /vol/proxy/ssl-dhparams.pem 2048
fi

# Avoid replacing these with envsubst
export host=\$host
export request_uri=\$request_uri

echo "Checking for fullchain.pem"
if [ ! -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
  echo "No SSL cert, enabling HTTP only..."
  envsubst < /etc/nginx/erp.conf.tpl > /etc/nginx/conf.d/default.conf
else
  echo "SSl cert exists, enabling HTTPS..."
  envsubst < /etc/nginx/erp-ssl.conf.tpl > /etc/nginx/conf.d/default.conf
fi

nginx -g "daemon off;"