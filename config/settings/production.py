from .base import *  # noqa
from .base import env

# Require explicit DATABASE_URL in production (no dev default from base).
DATABASES = {
    "default": {
        **env.db("DATABASE_URL"),
        "ATOMIC_REQUESTS": True,
        "TEST": {"NAME": "test_consultas_ciudadanas_db"},
    }
}

SECRET_KEY = env("DJANGO_SECRET_KEY")
#DEBUG = True

EMAIL_HOST = env("EMAIL_HOST", default=None)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="no-reply@visionciudadana.cegir.cl"
)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["visionciudadana.cegir.cl"])
CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", default=["https://visionciudadana.cegir.cl"]
)
if EMAIL_HOST:
    EMAIL_PORT = env("EMAIL_PORT")
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")


# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
#         "simple": {"format": "{levelname} {message}", "style": "{"},
#     },
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "DEBUG",
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#     },
# }