import pytest

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.models import Answer
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.tests.recipes import question_recipe


@pytest.mark.django_db
def test_bulk_create_answers(response):
    questions = [
        question_recipe.make(
            query_id=response.query_id, required=True, kind=QuestionConstants.KIND_TEXT
        )
        for _ in range(3)
    ]
    answers = [
        {
            "question_id": question.id,
            "response_id": response.id,
            "text": f"fake answer {index}",
        }
        for index, question in enumerate(questions)
    ]
    returned_instances = answer_providers.bulk_create_answers(answers=answers)
    assert all(isinstance(instance, Answer) for instance in returned_instances)
