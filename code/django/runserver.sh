python manage.py makemigrations;
python manage.py migrate;
python manage.py runserver_plus --cert-file /run/secrets/ssl_certificate --key-file /run/secrets/ssl_private_key;
