import pytest

from apps.public_queries.tests import recipes


@pytest.fixture
def public_query():
    return recipes.public_query_recipe.make()


@pytest.fixture
def question():
    return recipes.question_recipe.make()


@pytest.fixture
def response():
    return recipes.response_recipe.make()
