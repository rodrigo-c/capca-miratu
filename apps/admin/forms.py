from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import EmailField
from django.utils.translation import gettext_lazy

User = get_user_model()


class UserAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email"]
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": gettext_lazy("This email has already been taken.")},
        }
