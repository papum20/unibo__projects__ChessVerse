#!/bin/bash

python manage.py makemigrations;
python manage.py migrate;
python manage.py runsslserver --certificate /run/secrets/ssl_certificate.crt --key /run/secrets/ssl_priv_key.key 0.0.0.0:8000
