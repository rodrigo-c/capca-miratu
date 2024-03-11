from django.urls import path

from apps.admin.views import AdminEntryPoint, UserLoginView, UserLogoutView

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
]
