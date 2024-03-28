import pytest

from apps.public_queries.storages import (
    get_public_query_answer_image_path,
    get_public_query_image_path,
    get_public_query_question_image_path,
    get_public_query_question_option_image_path,
)


@pytest.mark.django_db
def test_get_public_query_answer_image_path(answer):
    url_code = answer.response.query.url_code
    filename = "file.jpg"
    assert (
        get_public_query_answer_image_path(answer, filename)
        == f"public_queries/{url_code}/answers/{answer.response_id}/{filename}"
    )


@pytest.mark.django_db
def test_get_public_query_image_path(public_query):
    filename = "file.jpg"
    assert (
        get_public_query_image_path(public_query, filename)
        == f"public_queries/{public_query.url_code}/images/{filename}"
    )


@pytest.mark.django_db
def test_get_public_query_question_image_path(question):
    url_code = question.query.url_code
    filename = "file.jpg"
    assert (
        get_public_query_question_image_path(question, filename)
        == f"public_queries/{url_code}/questions/{question.id}/{filename}"
    )


@pytest.mark.django_db
def test_get_public_query_question_option_image_path(question_option):
    url_code = question_option.question.query.url_code
    filename = "file.jpg"
    assert get_public_query_question_option_image_path(question_option, filename) == (
        f"public_queries/{url_code}/questions/"
        f"{question_option.question_id}/options/{question_option.id}/{filename}"
    )
