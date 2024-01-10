import pytest
from django.urls import reverse

from apps.public_queries.tests.recipes import public_query_recipe


@pytest.mark.django_db
class TestPublicQueryManager:
    def test_get(self, api_client, user):
        public_query = public_query_recipe.make()
        api_client.force_login(user)
        url = reverse(
            "admin_api:v1:public-query-list",
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["list"][0]["uuid"] == str(public_query.id)
