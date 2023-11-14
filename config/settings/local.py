from .base import *  # noqa
from .base import env

# General

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="LrFq7lIKzW9yHAQQJLOHr3bCKBTBs36panOjiv93WSph2szTliDRGwQxywWOw0kH",
)
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# Email

EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# Celery
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates

CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ALWAYS_EAGER = True

# Query Inspect
# https://github.com/dobarkod/django-queryinspect#configuration
MIDDLEWARE += ("qinspect.middleware.QueryInspectMiddleware",)  # noqa
QUERY_INSPECT_ENABLED = True
QUERY_INSPECT_LOG_STATS = True
QUERY_INSPECT_HEADER_STATS = True
QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_ABSOLUTE_LIMIT = None
QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = None
QUERY_INSPECT_LOG_TRACEBACKS = True
QUERY_INSPECT_DUPLICATE_MIN = 2
LOGGING["loggers"]["qinspect"] = {  # noqa
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": True,
}

# django-extensions
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa F405
