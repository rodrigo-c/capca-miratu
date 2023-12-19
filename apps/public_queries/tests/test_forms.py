import pytest

from apps.public_queries.forms import AnswerForm, ResponseForm
from apps.public_queries.lib.constants import QuestionConstants


@pytest.mark.django_db
class TestAnswerForm:
    def test_init(self, question_data):
        question_data.required = True
        form = AnswerForm(initial={"question-data": question_data})
        assert form.fields["text"].required == question_data.required
        assert form.question_data == question_data

    def test_get_validated_dataclasses(self, question_data):
        form = AnswerForm(
            initial={"question-data": question_data}, data={"text": "answer"}
        )
        assert form.is_valid()
        answer_data = form.get_validated_dataclass()
        assert answer_data.question_uuid == question_data.uuid

    def test_get_validated_dataclasses_with_image(self, question_data, uploaded_image):
        question_data.kind = QuestionConstants.KIND_IMAGE
        form = AnswerForm(
            initial={"question-data": question_data}, files={"image": uploaded_image}
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
