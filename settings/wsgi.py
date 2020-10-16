"""
WSGI config for qlsecret project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.chdir(cwd)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.configs')
application = get_wsgi_application()
