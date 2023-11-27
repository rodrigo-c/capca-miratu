import pytest

from apps.public_queries.lib.dataclasses import QuestionData
from apps.public_queries.tests import recipes
from apps.utils.dataclasses import build_dataclass_from_model_instance


@pytest.fixture
def public_query():
    return recipes.public_query_recipe.make()


@pytest.fixture
def question():
    return recipes.question_recipe.make()


@pytest.fixture
def question_data():
    question = recipes.question_recipe.make(required=True)
    return build_dataclass_from_model_instance(
        klass=QuestionData,
        instance=question,
        uuid=question.id,
        index=0,
        query_uuid=question.query_id,
    )


@pytest.fixture
def response():
    return recipes.response_recipe.make()
