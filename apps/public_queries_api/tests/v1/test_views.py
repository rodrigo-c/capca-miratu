import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestPublicQueryMapResult:
    def test_success(self, api_client, ended_public_query):
        url = reverse(
            "public_queries_api:v1:query-map-result-detail",
            kwargs={"pk": ended_public_query.url_code},
        )
        response = api_client.get(url)
        assert response.status_code == 200

    def test_not_found(self, api_client, ended_public_query):
        url = reverse(
            "public_queries_api:v1:query-map-result-detail",
            kwargs={"pk": 1},
        )
        response = api_client.get(url)
        assert response.status_code == 404
