"""
Production settings — extends base.py
Required env vars:
  DJANGO_SECRET_KEY   — long random string
  ALLOWED_HOSTS       — comma-separated domains, e.g. "erp.college.edu"
  EMAIL_HOST_USER     — SMTP user
  EMAIL_HOST_PASSWORD — SMTP password
  DATABASE_URL        — postgres://... (uncomment dj-database-url in base)
"""

import os
from .base import *  # noqa

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]   # crash fast if missing

# HTTPS enforcement
SECURE_SSL_REDIRECT         = True
SECURE_HSTS_SECONDS         = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD         = True
SESSION_COOKIE_SECURE       = True
CSRF_COOKIE_SECURE          = True
