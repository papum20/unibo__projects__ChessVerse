#!/bin/bash

python manage.py makemigrations;
python manage.py migrate;
python manage.py runserver 0.0.0.0:8000 #--certificate /run/secrets/ssl_cert --key /run/secrets/ssl_priv 0.0.0.0:8000
