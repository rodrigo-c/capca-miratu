from django.urls import path

from apps.public_queries.views import (
    PublicQueryDataResult,
    PublicQueryMapResult,
    PublicQuerySubmit,
    SuccessSubmit,
)

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
        "query/<str:uuid>/data",
        view=PublicQueryDataResult.as_view(),
        name="query-data",
    ),
    path(
        "query/<str:uuid>/map",
        view=PublicQueryMapResult.as_view(),
        name="query-map-result",
    ),
]
