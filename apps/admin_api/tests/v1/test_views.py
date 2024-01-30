from dataclasses import asdict
from unittest import mock

import pytest
from django.urls import reverse

from apps.public_queries.lib.constants import CreatePublicQueryConstants
from apps.public_queries.tests.recipes import (
    make_public_query_data,
    public_query_recipe,
)


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

    def _get_create_data(self) -> dict:
        public_query_data = make_public_query_data()
        data = asdict(public_query_data)
        for field in list(data):
            if data[field] is None:
                data.pop(field)
        for question in data["questions"]:
            question["options"] = question["options"] or []
        return data

    def test_create_success(self, api_client, user):
        api_client.force_login(user)
        url = reverse(f"{self.base_pattern}-list")
        data = self._get_create_data()
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == 200
        url = reverse(
            f"{self.base_pattern}-detail", kwargs={"pk": response.data["uuid"]}
        )
        assert api_client.get(url).status_code == 200

    @mock.patch("apps.public_queries.providers.public_query.create_public_query")
    def test_create_error(self, mock_create_public_query, api_client, user):
        api_client.force_login(user)
        url = reverse(f"{self.base_pattern}-list")
        data = self._get_create_data()
        mock_create_public_query.side_effect = ValueError
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == 400

    def test_create_with_invalid(self, api_client, user):
        api_client.force_login(user)
        url = reverse(f"{self.base_pattern}-list")
        data = self._get_create_data()
        data["start_at"] = "2000-02-01 20:00:00"
        data["end_at"] = "2000-01-01 20:00:00"
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == 400
        assert (
            str(response.data["non_field_errors"][0])
            == CreatePublicQueryConstants.INVALID_START_END_AT
        )
