#!/bin/bash

#set -e
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic

# gunicorn config.wsgi:application --bind 0.0.0.0:8000

#uwsgi --socket :8000 --master --enable-threads --module ERP_MASTER.wsgi
