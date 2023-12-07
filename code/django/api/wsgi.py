"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

<<<<<<< HEAD:code/django/api/wsgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_api.settings')
>>>>>>> dev-login:code/backend/backend_api/wsgi.py

application = get_wsgi_application()
