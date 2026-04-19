"""
WSGI config for core project (Vercel serverless compatible).
"""

import os
import sys

# Ensure 'backend/' is on the Python path so Django can find 'core.settings', 'api', etc.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application  # Vercel looks for 'app'

# Auto-run migrations on cold start (creates tables if they don't exist)
try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', interactive=False, verbosity=0)
except Exception as e:
    print(f"[wsgi] Migration warning: {e}")
