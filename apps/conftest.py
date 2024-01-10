import pytest
from rest_framework.test import APIClient

from model_bakery.recipe import Recipe


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return Recipe("users.User").make()
