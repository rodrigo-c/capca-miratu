import pytest
from django.urls import reverse

from apps.public_queries.lib.constants import AuthConstants, PublicQueryConstants
from apps.public_queries.tests.recipes import public_query_recipe, response_recipe


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


@pytest.mark.django_db
class TestPublicQueryDataResult:
    def test_success(self, api_client, ended_public_query):
        url = reverse(
            "public_queries_api:v1:query-data-result-detail",
            kwargs={"pk": ended_public_query.url_code},
        )
        response = api_client.get(url)
        assert response.status_code == 200

    def test_not_found(self, api_client, ended_public_query):
        url = reverse(
            "public_queries_api:v1:query-data-result-detail",
            kwargs={"pk": 1},
        )
        response = api_client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestPublicQueryAuth:
    def test_success(self, api_client):
        public_query = public_query_recipe.make(
            max_responses=2, auth_rut=PublicQueryConstants.AUTH_REQUIRED
        )
        repeated_rut = "10000000-8"
        response_recipe.make(query_id=public_query.id, rut=repeated_rut)

        url = reverse(
            "public_queries_api:v1:auth-can-submit",
            kwargs={"pk": public_query.url_code},
        )
        response = api_client.post(url, data={"rut": repeated_rut})
        assert response.status_code == 200

    def test_not_found(self, api_client):
        url = reverse(
            "public_queries_api:v1:auth-can-submit",
            kwargs={"pk": 1},
        )
        response = api_client.post(url)
        assert response.status_code == 404

    def test_email_required(self, api_client):
        public_query = public_query_recipe.make(
            auth_email=PublicQueryConstants.AUTH_REQUIRED
        )
        url = reverse(
            "public_queries_api:v1:auth-can-submit",
            kwargs={"pk": public_query.url_code},
        )
        response = api_client.post(url)
        assert response.status_code == 401
        response_data = response.json()
        assert response_data["email"] == AuthConstants.EMAIL_REQUIRED
