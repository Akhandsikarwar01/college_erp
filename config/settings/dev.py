"""
Development settings — extends base.py
Use: export DJANGO_SETTINGS_MODULE=config.settings.dev
"""

from .base import *  # noqa
import os

DEBUG = True
SECRET_KEY = "dev-insecure-key-do-not-use-in-prod"
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "testserver",
    "erp.akhandsikarwar.in",
    "college-erp-vlo5.onrender.com",
]

# Print emails to console by default; set SEND_REAL_EMAIL_IN_DEV=True to send real OTP emails
if os.environ.get("SEND_REAL_EMAIL_IN_DEV", "False") != "True":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# No manifest in dev (skip collectstatic)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Friendlier error pages
INSTALLED_APPS += []  # noqa: F405 — already in base, safe to repeat

# Django Debug Toolbar — uncomment if installed:
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]
