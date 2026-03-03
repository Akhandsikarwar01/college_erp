from .base import *

DEBUG = True
ALLOWED_HOSTS = []

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "erpmanager.akhand@gmail.com"
EMAIL_HOST_PASSWORD = "wkfc pfkf fygb wldu"  # spaces hata ke
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER