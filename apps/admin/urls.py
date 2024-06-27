from django.urls import path

from apps.admin.views import (
    AdminEntryPoint,
    UserLoginView,
    UserLogoutView,
    UserPasswordChangeView,
    UserPasswordResetConfirmView,
    UserPasswordResetView,
)

app_name = "admin"

urlpatterns = [
    path(
        "",
        view=AdminEntryPoint.as_view(),
        name="entry-point",
    ),
    path(
        "login/",
        view=UserLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        view=UserLogoutView.as_view(),
        name="logout",
    ),
    path(
        "password_change/",
        view=UserPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_reset/",
        view=UserPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "~reset/<uidb64>/<token>/",
        UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
