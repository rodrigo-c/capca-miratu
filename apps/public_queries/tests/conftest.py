import pytest

from apps.public_queries.lib.constants import PublicQueryConstants
from apps.public_queries.lib.dataclasses import QuestionData
from apps.public_queries.tests import recipes
from apps.public_queries.utils import create_fake_uploaded_image
from apps.utils.dataclasses import build_dataclass_from_model_instance


@pytest.fixture
def public_query():
    return recipes.public_query_recipe.make()


@pytest.fixture
def inactive_public_query():
    return recipes.public_query_recipe.make(active=False)


@pytest.fixture
def question():
    return recipes.question_recipe.make()


@pytest.fixture
def question_option():
    return recipes.question_option_recipe.make()


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


@pytest.fixture
def answer():
    return recipes.answer_recipe.make()


@pytest.fixture
def answer_with_option():
    answer = recipes.answer_recipe.make()
    option = recipes.question_option_recipe.make(
        question_id=answer.question_id,
    )
    answer.options.add(option.id)
    return answer


@pytest.fixture
def uploaded_image(field_name="images", size=(50, 50), color=(256, 0, 0)):
    return create_fake_uploaded_image(field_name=field_name, size=size, color=color)


@pytest.fixture
def ended_public_query(uploaded_image):
    return recipes.make_ended_public_query(uploaded_image=uploaded_image)


@pytest.fixture
def closed_public_query():
    public_query = recipes.public_query_recipe.make(
        kind=PublicQueryConstants.KIND_CLOSED,
    )
    return public_query


@pytest.fixture
def make_closed_public_query():
    def _make_closed_public_query(emails):
        public_query = recipes.public_query_recipe.make(
            kind=PublicQueryConstants.KIND_CLOSED,
        )
        for email in emails:
            responder = recipes.responder_recipe.make(email=email)
            public_query.allowed_responders.add(responder.id)
        return public_query

    return _make_closed_public_query
