from django.contrib.gis.geos import Point

from model_bakery.recipe import Recipe, foreign_key

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.public_queries.utils import create_fake_uploaded_image

public_query_recipe = Recipe(
    "public_queries.PublicQuery",
    kind=PublicQueryConstants.KIND_OPEN,
    active=True,
)

question_recipe = Recipe(
    "public_queries.Question",
    kind=QuestionConstants.KIND_TEXT,
    query=foreign_key(public_query_recipe),
)

question_select_recipe = question_recipe.extend(
    kind=QuestionConstants.KIND_SELECT,
)

question_option_recipe = Recipe(
    "public_queries.QuestionOption",
    question=foreign_key(question_select_recipe),
)

response_recipe = Recipe(
    "public_queries.Response", query=foreign_key(public_query_recipe)
)

answer_recipe = Recipe(
    "public_queries.Answer",
    response=foreign_key(response_recipe),
)


def make_ended_public_query(uploaded_image=None):
    uploaded_image = uploaded_image or create_fake_uploaded_image()
    public_query = public_query_recipe.make(active=True)
    questions = [
        question_recipe.make(query_id=public_query.id),
        question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_IMAGE,
        ),
        question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_SELECT,
        ),
        question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_POINT,
        ),
    ]
    options = [
        question_option_recipe.make(question_id=questions[2].id, order=index)
        for index in range(5)
    ]
    responses = []
    for index in range(16):
        kwargs = (
            {}
            if index % 2 == 0
            else {"email": f"fake_{index}@email.com", "rut": f"100000{index}-1"}
        )
        response = response_recipe.make(
            query_id=public_query.id, location=Point(1, 1), **kwargs
        )
        responses.append(response)
        for question in questions:
            answer = answer_recipe.make(
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
