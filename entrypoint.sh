#!/bin/bash

#set -e
python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input

gunicorn ERP_MASTER.wsgi:application --bind 0.0.0.0:8000

#uwsgi --socket :8000 --master --enable-threads --module ERP_MASTER.wsgi



# https://www.youtube.com/watch?v=3_ZJWlf25bY

#