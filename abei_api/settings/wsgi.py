"""
WSGI config for qlsecret project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

wd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    __import__('abei')
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(wd, os.pardir)))

os.chdir(wd)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.configs')
application = get_wsgi_application()
