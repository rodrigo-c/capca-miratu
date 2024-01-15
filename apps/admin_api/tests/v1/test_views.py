import pytest
from django.urls import reverse

from apps.public_queries.tests.recipes import public_query_recipe


@pytest.mark.django_db
class TestPublicQueryManager:
    base_pattern = "admin_api:v1:public-query"

    def test_get_list(self, api_client, user):
        public_query = public_query_recipe.make()
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-list",
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["list"][0]["uuid"] == str(public_query.id)

    def test_get_retrieve(self, api_client, user, ended_public_query):
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-detail", kwargs={"pk": ended_public_query.url_code}
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["query"]["uuid"] == str(ended_public_query.id)

    def test_get_retrieve_not_found(self, api_client, user):
        api_client.force_login(user)
        url = reverse(f"{self.base_pattern}-detail", kwargs={"pk": "x"})
        response = api_client.get(url)
        assert response.status_code == 404
