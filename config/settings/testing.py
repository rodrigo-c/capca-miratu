from .base import *  # noqa
from .base import env

# General

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="1WGGfJ4kTONxe99XtiJ9SASF5Hz1VBouFdv3hm8AtdWwHcg5YkXIXwWAcHLcXREl",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa
