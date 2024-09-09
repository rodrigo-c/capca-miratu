from django.urls import path
from django.views.generic.base import RedirectView

from apps.public_queries.views import PublicQuerySubmit, SuccessSubmit

app_name = "public_queries"

urlpatterns = [
    path(
        "submit/<str:uuid>",
        view=PublicQuerySubmit.as_view(),
        name="submit",
    ),
    path(
        "submitted/<str:uuid>",
        view=SuccessSubmit.as_view(),
        name="submit-success",
    ),
    path(
        "",
        view=RedirectView.as_view(url="/admin/"),
        name="root",
    ),
]
