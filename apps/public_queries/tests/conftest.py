import pytest
from django.contrib.gis.geos import Point

from apps.public_queries.lib.constants import QuestionConstants
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
    public_query = recipes.public_query_recipe.make(active=True)
    questions = [
        recipes.question_recipe.make(query_id=public_query.id),
        recipes.question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_IMAGE,
        ),
        recipes.question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_SELECT,
        ),
        recipes.question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_POINT,
        ),
    ]
    options = [
        recipes.question_option_recipe.make(question_id=questions[2].id, order=index)
        for index in range(5)
    ]
    responses = []
    for index in range(16):
        kwargs = (
            {}
            if index % 2 == 0
            else {"email": f"fake_{index}@email.com", "rut": f"100000{index}-1"}
        )
        response = recipes.response_recipe.make(
            query_id=public_query.id, location=Point(1, 1), **kwargs
        )
        responses.append(response)
        for question in questions:
            answer = recipes.answer_recipe.make(
                response_id=response.id,
                question_id=question.id,
                text=(
                    f"Fake Text {index}"
                    if question.kind == QuestionConstants.KIND_TEXT
                    else None
                ),
                image=(
                    uploaded_image
                    if question.kind == QuestionConstants.KIND_IMAGE
                    else None
                ),
                _create_files=(question.kind == QuestionConstants.KIND_IMAGE),
                point=(
                    Point(1, 1)
                    if question.kind == QuestionConstants.KIND_POINT
                    else None
                ),
            )
            if question.kind == QuestionConstants.KIND_SELECT:
                answer.options.add(options[1 if index % 2 == 0 else 2].id)
    return public_query
