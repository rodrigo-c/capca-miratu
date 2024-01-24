import pytest
from rest_framework.test import APIClient

from model_bakery.recipe import Recipe

from apps.public_queries.tests import recipes as public_query_recipes
from apps.public_queries.utils import create_fake_uploaded_image


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return Recipe("users.User").make()


@pytest.fixture
def ended_public_query():
    uploaded_image = create_fake_uploaded_image(
        field_name="images", size=(50, 50), color=(256, 0, 0)
    )
    return public_query_recipes.make_ended_public_query(uploaded_image=uploaded_image)
