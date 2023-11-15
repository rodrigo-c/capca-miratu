from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from apps.admin.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()


class UserAdmin(UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ["password"]}),
        (("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "first_name", "last_name", "is_superuser", "is_staff"]
    search_fields = ["email"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


class GroupAdmin(ModelAdmin):
    pass


users_tuple_models = [
    (User, UserAdmin),
    (Group, GroupAdmin),
]
