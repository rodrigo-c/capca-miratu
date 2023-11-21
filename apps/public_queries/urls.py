from django.urls import path

from apps.public_queries.views import PublicQuerySubmit

app_name = "public_queries"

urlpatterns = [
    path(
        "submit/<str:uuid>",
        view=PublicQuerySubmit.as_view(),
        name="submit",
    ),
]
