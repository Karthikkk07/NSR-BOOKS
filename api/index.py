"""
Vercel Serverless Entry Point for the Django backend.

Vercel detects this file automatically as the API handler for all /api/* routes.
This file MUST be at the project root in an 'api/' folder.
"""
import sys
import os

# Add the backend directory to the path so Django can find its modules
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application

# Run migrations on first cold start
try:
    _app = get_wsgi_application()
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', interactive=False, verbosity=0)
except Exception as e:
    print(f"[api/index.py] startup error: {e}")
    _app = get_wsgi_application()

app = _app
