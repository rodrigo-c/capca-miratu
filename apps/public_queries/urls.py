from django.urls import path

from apps.public_queries.views import (
    AnswerQuestionResult,
    PublicQueryMapResult,
    PublicQueryResponseResult,
    PublicQueryResult,
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
        "query/<str:uuid>/result",
        view=PublicQueryResult.as_view(),
        name="query-result",
    ),
    path(
        "query/<str:uuid>/map",
        view=PublicQueryMapResult.as_view(),
        name="query-map-result",
    ),
    path(
        "question/<str:uuid>/result",
        view=AnswerQuestionResult.as_view(),
        name="answer-result",
    ),
    path(
        "responses/<str:uuid>/result",
        view=PublicQueryResponseResult.as_view(),
        name="response-result",
    ),
]
