"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
app = application

# Run migrations automatically on startup (Serverless friendly)
from django.core.management import call_command
try:
    print("Running migrations...")
    call_command('migrate', interactive=False)
    print("Migrations complete.")
except Exception as e:
    print(f"Migration error: {e}")

