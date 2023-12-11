from django.urls import path

from apps.public_queries.views import (
    AnswerQuestionResult,
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
        "question/<str:uuid>/result",
        view=AnswerQuestionResult.as_view(),
        name="answer-result",
    ),
]
