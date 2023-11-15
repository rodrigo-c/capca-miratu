from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField
from django.utils.translation import gettext_lazy

from apps.users.managers import UserManager


class User(AbstractUser):
    email = EmailField(gettext_lazy("email address"), unique=True)
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
