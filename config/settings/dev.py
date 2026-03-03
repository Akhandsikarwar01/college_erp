from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "college-erp-vlo5.onrender.com",
    "akhandsikarwar.in",
    "www.akhandsikarwar.in",
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "erpmanager.akhand@gmail.com"
EMAIL_HOST_PASSWORD = "wkfc pfkf fygb wldu"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER