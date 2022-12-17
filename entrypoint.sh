#!/bin/bash

#set -e
# python3 manage.py makemigrations --no-input
# python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input

# gunicorn config.wsgi:application --bind 0.0.0.0:8001

#uwsgi --socket :8000 --master --enable-threads --module ERP_MASTER.wsgi
