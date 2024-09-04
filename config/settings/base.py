from pathlib import Path

import environ

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "apps"

env = environ.Env()

# General

DEBUG = env.bool("DJANGO_DEBUG", default=False)
LANGUAGE_CODE = "en-us"
SITE_ID = 1
TIME_ZONE = "America/Santiago"
USE_TZ = True

# Database

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["TEST"] = {"NAME": "test_consultas_ciudadanas_db"}

# URLs

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Apps

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

THIRD_PARTY_APPS = [
    "nested_inline",
    "rest_framework",
    "django_extensions",
    "storages",
]

LOCAL_APPS = [
    "apps.users",
    "apps.admin.apps.AdminConfig",
    "apps.public_queries",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication

LOGIN_URL = "/admin/login/"
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
# https://docs.djangoproject.com/en/4.2/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
_VALIDATION_PATH = "django.contrib.auth.password_validation"
VALIDATOR_NAMES = [
    "UserAttributeSimilarityValidator",
    "MinimumLengthValidator",
    "CommonPasswordValidator",
    "NumericPasswordValidator",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{_VALIDATION_PATH}.{validator_name}"}
    for validator_name in VALIDATOR_NAMES
]

# Middleware

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Static

STATIC_URL = "static/"
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
STATICFILES_DIRS = [str(ROOT_DIR / "static")]

# Media

MEDIA_URL = "media/"
MEDIA_ROOT = str(ROOT_DIR / "media")

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default=None)
if AWS_ACCESS_KEY_ID:
    STATIC_LOCATION = "static"
    PUBLIC_MEDIA_LOCATION = "media"
    PRIVATE_MEDIA_LOCATION = "private"
    AWS_DEFAULT_ACL = None
    STORAGES = {
        "default": {
            "BACKEND": "config.storages.PublicMediaStorage",
        },
        "staticfiles": {
            "BACKEND": "config.storages.StaticStorage",
        },
        "private": {
            "BACKEND": "config.storages.PrivateMediaStorage",
        },
    }
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = "us-east-2"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    STATIC_LOCATION = "static"
    PUBLIC_MEDIA_LOCATION = "media"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/"
    AWS_QUERYSTRING_EXPIRE = 3600
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_REGION_NAME = "us-east-2"

# Template

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["apps/admin/templates"],  # TODO: disable django admin
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# Security

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "SAMEORIGIN"

# Email

EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_TIMEOUT = 5

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "werkzeug": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
        "django.template": {
            "handlers": ["console"],
            "propagate": True,
            "level": "WARN",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ]
}
