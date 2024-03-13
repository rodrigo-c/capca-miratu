from dataclasses import asdict
from unittest import mock

import pytest
from django.urls import reverse

from apps.public_queries.lib.constants import (
    CreatePublicQueryConstants,
    PublicQueryConstants,
)
from apps.public_queries.tests.recipes import (
    make_public_query_data,
    public_query_recipe,
)


@pytest.mark.django_db
class TestPublicQueryManager:
    base_pattern = "admin_api:v1:public-query"

    def test_get_list(self, api_client, user):
        public_query = public_query_recipe.make(created_by_id=user.id)
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-list",
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["list"][0]["uuid"] == str(public_query.id)

    def test_list_filtered(self, api_client, user):
        public_query_recipe.make(created_by_id=None)
        public_query = public_query_recipe.make(created_by_id=user.id)
        url = reverse(
            f"{self.base_pattern}-list",
        )
        api_client.force_login(user)
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["list"][0]["uuid"] == str(public_query.id)
        assert len(response.data["list"]) == 1

    def test_get_retrieve(self, api_client, user, ended_public_query):
        ended_public_query.created_by_id = user.id
        ended_public_query.save()
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
            str(response.data["start_at"][0])
            == CreatePublicQueryConstants.INVALID_START_END_AT
        )

    def test_update_success(self, api_client, user, ended_public_query):
        ended_public_query.created_by_id = user.id
        ended_public_query.save()
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-detail", kwargs={"pk": ended_public_query.url_code}
        )
        data = self.get_update_data(public_query=ended_public_query)
        response = api_client.put(url, data=data, format="json")
        assert response.status_code == 200
        ended_public_query.refresh_from_db()
        for field, value in data.items():
            if field != "questions":
                assert getattr(ended_public_query, field) == value
        refreshed_questions = list(ended_public_query.questions.all())
        for index, question in enumerate(refreshed_questions):
            assert question.name == f"Question {index}"
            if question.kind == "SELECT":
                assert question.options.first().name == "new"

    @mock.patch("apps.public_queries.providers.question.bulk_update_questions")
    def test_update_error(
        self, mock_update_public_query, api_client, user, ended_public_query
    ):
        ended_public_query.created_by_id = user.id
        ended_public_query.save()
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-detail", kwargs={"pk": ended_public_query.url_code}
        )
        mock_update_public_query.side_effect = ValueError
        data = self.get_update_data(ended_public_query)
        response = api_client.put(url, data=data, format="json")
        assert response.status_code == 400

    def get_update_data(self, public_query):
        data = {
            "name": "public_query_modified",
            "description": "_modified",
            "active": not public_query.active,
            "max_responses": 10,
            "auth_rut": PublicQueryConstants.AUTH_REQUIRED,
            "auth_email": PublicQueryConstants.AUTH_REQUIRED,
        }
        questions = []
        for index, question in enumerate(public_query.questions.all()):
            question_data = {
                "kind": question.kind,
                "query_uuid": public_query.id,
                "uuid": question.id if index > 0 else None,
                "name": f"Question {index}",
                "description": question.description,
                "order": index,
                "required": question.required,
            }
            if question.kind == "SELECT":
                question_data["options"] = [
                    {
                        "name": option.name if i > 0 else "new",
                        "uuid": option.id if i > 0 else None,
                        "question_uuid": question.id,
                        "order": i,
                    }
                    for i, option in enumerate(question.options.all())
                ]
            questions.append(question_data)
        data["questions"] = questions
        return data

    def test_get_map(self, api_client, user, ended_public_query):
        ended_public_query.created_by_id = user.id
        ended_public_query.save()
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-map", kwargs={"pk": ended_public_query.url_code}
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["query"]["uuid"] == str(ended_public_query.id)
        assert len(response.data["point_list"]) == 16

    def test_get_map_not_found(self, api_client, user, ended_public_query):
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-map", kwargs={"pk": ended_public_query.url_code}
        )
        response = api_client.get(url)
        assert response.status_code == 404

    def test_get_data(self, api_client, user, ended_public_query):
        ended_public_query.created_by_id = user.id
        ended_public_query.save()
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-data", kwargs={"pk": ended_public_query.url_code}
        )
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data["query"]["uuid"] == str(ended_public_query.id)
        assert len(response.data["dataset"]) == 16

    def test_get_data_not_found(self, api_client, user, ended_public_query):
        api_client.force_login(user)
        url = reverse(
            f"{self.base_pattern}-data", kwargs={"pk": ended_public_query.url_code}
        )
        response = api_client.get(url)
        assert response.status_code == 404
