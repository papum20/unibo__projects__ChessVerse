"""
ASGI config for myproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

<<<<<<< HEAD:code/django/api/asgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_api.settings')
>>>>>>> dev-login:code/backend/backend_api/asgi.py

application = get_asgi_application()
