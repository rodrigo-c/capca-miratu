from django.urls import include, path

app_name = "mobile_api"

urlpatterns = [
    path("v1/", include("apps.mobile_api.v1.urls", namespace="v1")),
]
