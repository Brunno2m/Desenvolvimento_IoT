"""WSGI config for fleet_front project."""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleet_front.settings")

application = get_wsgi_application()
