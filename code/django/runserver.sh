#!/bin/bash

python manage.py makemigrations;
python manage.py migrate;
python manage.py runsslserver --certificate /run/secrets/api_cert --key /run/secrets/api_priv 0.0.0.0:8000
