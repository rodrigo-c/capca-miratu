from .base import *  # noqa
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY")


EMAIL_HOST = env("EMAIL_HOST", default=None)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@vision.cegirapp.cl")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["vision.cegirapp.com"])
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=["https://vision.cegirapp.com"]
)
if EMAIL_HOST:
    EMAIL_PORT = env("EMAIL_PORT")
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
