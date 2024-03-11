from datetime import datetime
from uuid import uuid4

import pytest
from django.urls import reverse
from django.utils.timezone import make_aware

from freezegun import freeze_time

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.tests.recipes import (
    public_query_recipe,
    question_option_recipe,
    question_recipe,
)


@pytest.mark.django_db
class TestPublicQuerySubmit:
    public_query_pattern = "public_queries:submit"

    def test_get_success(self, client):
        public_query = public_query_recipe.make(active=True)
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        response = client.get(url)
        assert response.status_code == 200

    def test_get_success_with_url_code(self, client):
        public_query = public_query_recipe.make(active=True)
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.url_code})
        response = client.get(url)
        assert response.status_code == 200

    def test_get_success_with_closed(self, client, make_closed_public_query):
        valid_email = "valid@ema.il"
        public_query = make_closed_public_query(emails=[valid_email])
        secret_key = public_query.allowedresponder_set.first().email_code
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.url_code})
        url += f"?e={valid_email}&k={secret_key}"
        response = client.get(url)
        assert response.status_code == 200

    def test_get_not_authorized_with_closed(self, client, make_closed_public_query):
        valid_email = "valid@ema.il"
        public_query = make_closed_public_query(emails=[valid_email])
        secret_key = public_query.allowedresponder_set.first().email_code[:-2]
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.url_code})
        url += f"?e={valid_email}&k={secret_key}"
        response = client.get(url)
        assert response.status_code == 404

    def test_get_with_closed_and_without_auth_params(
        self, client, make_closed_public_query
    ):
        public_query = make_closed_public_query(emails=[])
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        response = client.get(url)
        assert response.status_code == 404

    def test_get_not_active(self, client):
        public_query = public_query_recipe.make(active=False)
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        response = client.get(url)
        assert response.status_code == 404

    def test_get_not_active_with_url_code(self, client):
        public_query = public_query_recipe.make(active=False)
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.url_code})
        response = client.get(url)
        assert response.status_code == 404

    def test_out_of_start_time(self, client):
        public_query = public_query_recipe.make(
            active=True, start_at=make_aware(datetime(2023, 1, 2))
        )
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        with freeze_time("2023-01-01"):
            response = client.get(url)
        assert response.status_code == 404

    def test_get_with_questions(self, client):
        public_query = public_query_recipe.make(active=True)
        questions = [
            question_recipe.make(query_id=public_query.id) for index in range(5)
        ]
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "answer_formset" in response.context
        for index, form in enumerate(response.context["answer_formset"].forms):
            assert form.question_data.uuid == questions[index].id

    def test_post_with_question_errors(self, client):
        public_query = public_query_recipe.make(active=True)
        questions = [
            question_recipe.make(query_id=public_query.id, required=True)
            for index in range(5)
        ]
        data = {
            "rut": "",
            "email": "",
            "form-TOTAL_FORMS": 5,
            "form-INITIAL_FORMS": 5,
            "query": public_query.id,
        }
        for index, question in enumerate(questions):
            data[f"form-{index}-question"] = str(question.id)
            data[f"form-{index}-text"] = ""
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        http_response = client.post(url, data=data)
        assert http_response.status_code == 200
        for error in http_response.context["answer_formset"].errors:
            assert "text" in error
            assert error["text"] == ["This field is required."]

    def test_post_with_response_error(self, client):
        public_query = public_query_recipe.make(active=True)
        questions = [
            question_recipe.make(query_id=public_query.id, required=True)
            for index in range(5)
        ]
        data = {
            "rut": "",
            "email": "x",
            "form-TOTAL_FORMS": 5,
            "form-INITIAL_FORMS": 5,
            "query": public_query.id,
        }
        for index, question in enumerate(questions):
            data[f"form-{index}-question"] = str(question.id)
            data[f"form-{index}-text"] = "r"
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        http_response = client.post(url, data=data)
        assert http_response.status_code == 200
        assert "email" in http_response.context_data["response_form"].errors
        assert http_response.context_data["response_form"].errors["email"] == [
            "Enter a valid email address."
        ]

    def test_post_success(self, client, uploaded_image):
        public_query = public_query_recipe.make(active=True)
        questions = [
            question_recipe.make(query_id=public_query.id),
            question_recipe.make(
                query_id=public_query.id,
                kind=QuestionConstants.KIND_IMAGE,
            ),
            question_recipe.make(
                query_id=public_query.id,
                kind=QuestionConstants.KIND_SELECT,
            ),
            question_recipe.make(
                query_id=public_query.id,
                kind=QuestionConstants.KIND_POINT,
            ),
        ]
        options = [
            question_option_recipe.make(question_id=questions[2].id, order=index)
            for index in range(5)
        ]

        test_text = "test"
        data = {
            "rut": "100000-2",
            "email": "fake@email.com",
            "form-TOTAL_FORMS": 4,
            "form-INITIAL_FORMS": 4,
            "query": public_query.id,
            "form-0-text": test_text,
            "form-1-image": uploaded_image,
            "form-2-options": [str(options[0].id)],
            "form-3-point": '{"type":"Point","coordinates":[1, 1]}',
        }

        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        http_response = client.post(url, data=data)
        assert http_response.status_code == 302
        created_response = public_query.responses.first()
        assert created_response.email == data["email"]
        assert created_response.rut == data["rut"]
        assert str(created_response.id) == http_response.url[11:]
        created_answers = list(created_response.answers.all())

        assert created_answers[0].text == test_text
        assert uploaded_image.name[:-4] in created_answers[1].image.name
        assert (
            created_answers[2].options.values_list("id", flat=True)[0] == options[0].id
        )


@pytest.mark.django_db
class TestSuccessSubmit:
    public_query_pattern = "public_queries:submit-success"

    def test_success(self, client, response):
        url = reverse(self.public_query_pattern, kwargs={"uuid": response.id})
        http_response = client.get(url)
        assert http_response.status_code == 200

    def test_not_found_invalid_uuid(self, client):
        url = reverse(self.public_query_pattern, kwargs={"uuid": "x"})
        http_response = client.get(url)
        assert http_response.status_code == 404

    def test_not_found_unknown_uuid(self, client):
        url = reverse(self.public_query_pattern, kwargs={"uuid": uuid4()})
        http_response = client.get(url)
        assert http_response.status_code == 404


@pytest.mark.django_db
class TestPublicQueryMapResult:
    public_query_pattern = "public_queries:query-map-result"

    def test_success(self, client, ended_public_query):
        url = reverse(
            self.public_query_pattern, kwargs={"uuid": ended_public_query.url_code}
        )
        http_response = client.get(url)
        assert http_response.status_code == 200


@pytest.mark.django_db
class TestPublicQueryDataResult:
    public_query_pattern = "public_queries:query-data"

    def test_success(self, client, ended_public_query):
        url = reverse(
            self.public_query_pattern, kwargs={"uuid": ended_public_query.url_code}
        )
        http_response = client.get(url)
        assert http_response.status_code == 200
