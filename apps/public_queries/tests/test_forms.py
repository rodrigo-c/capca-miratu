from unittest import mock

import pytest

from apps.public_queries.forms import AnswerForm, ResponseForm


@pytest.mark.django_db
class TestAnswerForm:
    def test_init(self):
        fake_question_data = mock.Mock()
        fake_question_data.required = True
        form = AnswerForm(initial={"question-data": fake_question_data})
        assert form.fields["text"].required == fake_question_data.required
        assert form.question_data == fake_question_data

    def test_get_validated_dataclass(self, question_data):
        form = AnswerForm(
            initial={"question-data": question_data}, data={"text": "answer"}
        )
        assert form.is_valid()
        answer_data = form.get_validated_dataclass()
        assert answer_data.question_uuid == question_data.uuid


@pytest.mark.django_db
class TestResponseForm:
    def test_get_validated_dataclass(self, public_query):
        form = ResponseForm(data={"email": ""})
        form.is_valid()
        response_data = form.get_validated_dataclass(
            query_uuid=public_query.id, answers=[]
        )
        assert response_data.query_uuid == public_query.id
