import pytest
from rest_framework.test import APIClient

from apps.public_queries.tests.recipes import make_ended_public_query


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def ended_public_query():
    return make_ended_public_query()
