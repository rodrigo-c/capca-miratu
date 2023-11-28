from io import BytesIO

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

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
        answer_data_list = form.get_validated_dataclasses()
        assert answer_data_list[0].question_uuid == question_data.uuid

    def test_get_validated_dataclasses_with_image(self, question_data):
        question_data.kind = QuestionConstants.KIND_IMAGE
        image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
        image_file = BytesIO()
        image.save(image_file, "PNG")
        image_file.seek(0)
        image_file = InMemoryUploadedFile(
            image_file,
            name="fake-image.png",
            field_name="images",
            content_type="image/png",
            size=len(image_file.getvalue()),
            charset=None,
        )
        form = AnswerForm(
            initial={"question-data": question_data}, files={"images": [image_file]}
        )
        assert form.is_valid()
        answer_data_list = form.get_validated_dataclasses()
        assert answer_data_list[0].question_uuid == question_data.uuid


@pytest.mark.django_db
class TestResponseForm:
    def test_get_validated_dataclass(self, public_query):
        form = ResponseForm(data={"email": ""})
        form.is_valid()
        response_data = form.get_validated_dataclass(
            query_uuid=public_query.id, answers=[]
        )
        assert response_data.query_uuid == public_query.id
