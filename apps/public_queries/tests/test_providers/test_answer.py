import pytest

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.models import Answer
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.tests.recipes import question_recipe


@pytest.mark.django_db
def test_bulk_create_answers(response, uploaded_image):
    questions = [
        question_recipe.make(
            query_id=response.query_id, required=True, kind=QuestionConstants.KIND_TEXT
        )
        for _ in range(2)
    ]
    image_question = question_recipe.make(
        query_id=response.query_id, required=True, kind=QuestionConstants.KIND_IMAGE
    )
    answers = [
        {
            "question_id": question.id,
            "response_id": response.id,
            "text": f"fake answer {index}",
        }
        for index, question in enumerate(questions)
    ]
    image_answer = {
        "question_id": image_question.id,
        "response_id": response.id,
        "image": uploaded_image,
    }
    answers.append(image_answer)
    returned_instances = answer_providers.bulk_create_answers(answers=answers)
    assert all(isinstance(instance, Answer) for instance in returned_instances)
    assert returned_instances[-1].thumb.url
    assert returned_instances[-1].thumb_medium.url


@pytest.mark.django_db
def test_get_total_answers_by_question_uuid(answer):
    assert (
        answer_providers.get_total_answers_by_question_uuid(
            question_uuid=answer.question_id
        )
        == 1
    )


@pytest.mark.django_db
def test_get_answers_by_question_uuid(answer):
    returned_instances = answer_providers.get_answers_by_question_uuid(
        question_uuid=answer.question_id
    )
    assert returned_instances[0].id == answer.id


@pytest.mark.django_db
def test_get_answers_by_query_uuid(answer):
    returned_instances = answer_providers.get_answers_by_query_uuid(
        query_uuid=answer.question.query_id
    )
    assert returned_instances[0].id == answer.id


@pytest.mark.django_db
def test_get_total_answers_by_option_uuid(answer_with_option):
    option_uuid = answer_with_option.options.first().id
    assert (
        answer_providers.get_total_answers_by_option_uuid(option_uuid=option_uuid) == 1
    )
