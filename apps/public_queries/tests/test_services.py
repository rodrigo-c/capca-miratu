from datetime import datetime
from tempfile import NamedTemporaryFile

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.timezone import make_aware

from freezegun import freeze_time

from apps.public_queries import services
from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PublicQueryData,
    QuestionData,
    ResponseData,
)
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.tests.recipes import (
    public_query_recipe,
    question_option_recipe,
    question_recipe,
)


@pytest.mark.django_db
def test_get_public_query_by_uuid(public_query):
    public_query_data = services.get_public_query_by_uuid(uuid=public_query.id)
    assert isinstance(public_query_data, PublicQueryData)
    assert public_query_data.uuid == public_query.id
    assert public_query_data.active is True
    assert isinstance(public_query_data.name, str)
    assert public_query_data.image is None


@pytest.mark.django_db
class TestGetActivePublicQueryByUUID:
    def test_success(self):
        public_query = public_query_recipe.make(active=True)
        public_query_data = services.get_active_public_query_by_uuid(
            uuid=public_query.id
        )
        assert isinstance(public_query_data, PublicQueryData)
        assert public_query_data.uuid == public_query.id
        assert isinstance(public_query_data.name, str)
        assert public_query_data.image is None

    def test_with_questions(self):
        public_query = public_query_recipe.make(active=True)
        questions = [
            question_recipe.make(query_id=public_query.id) for index in range(5)
        ]
        public_query_data = services.get_active_public_query_by_uuid(
            uuid=public_query.id
        )
        for index, question in enumerate(questions):
            question_data = public_query_data.questions[index]
            assert isinstance(question_data, QuestionData)
            assert question.id == question_data.uuid
            assert question.query_id == question_data.query_uuid
            assert index == question_data.index

    def test_with_questions_with_options(self):
        public_query = public_query_recipe.make(active=True)
        select_question = question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_SELECT,
        )
        option = question_option_recipe.make(question_id=select_question.id)
        public_query_data = services.get_active_public_query_by_uuid(
            uuid=public_query.id
        )
        question_data = public_query_data.questions[0]
        option_data = question_data.options[0]
        assert option_data.uuid == option.id
        assert option_data.name == option.name

    def test_out_of_start_time(self):
        public_query = public_query_recipe.make(
            active=True, start_at=make_aware(datetime(2023, 1, 2))
        )
        with freeze_time("2023-01-01"):
            with pytest.raises(PublicQueryDoesNotExist):
                services.get_active_public_query_by_uuid(uuid=public_query.id)

    def test_out_of_end_time(self):
        public_query = public_query_recipe.make(
            active=True, end_at=make_aware(datetime(2023, 1, 1))
        )
        with freeze_time("2023-01-02"):
            with pytest.raises(PublicQueryDoesNotExist):
                services.get_active_public_query_by_uuid(uuid=public_query.id)


@pytest.mark.django_db
def test_get_public_query_by_url_code(public_query):
    returned_query = services.get_active_public_query_by_url_code(
        url_code=public_query.url_code
    )
    assert returned_query.uuid == public_query.id
    assert isinstance(returned_query, PublicQueryData)


@pytest.mark.django_db
def test_get_response_by_uuid(response):
    response_data = services.get_response_by_uuid(uuid=response.id)
    assert response_data.uuid == response.id
    assert isinstance(response_data, ResponseData)
    assert isinstance(response_data.query_data, PublicQueryData)


@pytest.mark.django_db
class TestSubmitResponse:
    def test_success(self):
        public_query = public_query_recipe.make(active=True)
        questions = [
            question_recipe.make(query_id=public_query.id, order=index)
            for index in range(5)
        ]
        answer_data_list = [
            AnswerData(
                question_uuid=question.id, text=f"fake response {question.order}"
            )
            for question in questions
        ]
        response_data = ResponseData(
            query_uuid=public_query.id,
            answers=answer_data_list,
        )
        returned_response = services.submit_response(response=response_data)

        assert returned_response.uuid
        assert all(answer.uuid for answer in returned_response.answers)
        assert returned_response.uuid == public_query.responses.first().id

    def test_success_with_image(self):
        public_query = public_query_recipe.make(active=True)
        image_question = question_recipe.make(
            query_id=public_query.id, order=0, kind=QuestionConstants.KIND_IMAGE
        )
        with NamedTemporaryFile() as image_file:
            answer_data = AnswerData(
                question_uuid=image_question.id,
                image=InMemoryUploadedFile(
                    image_file,
                    name="fake-image.png",
                    field_name="form-field",
                    content_type="image/png",
                    size=1,
                    charset=None,
                ),
            )
            response_data = ResponseData(
                query_uuid=public_query.id,
                answers=[answer_data],
            )
            returned_response = services.submit_response(response=response_data)

        assert returned_response.uuid
        assert all(answer.uuid and answer.image for answer in returned_response.answers)
        assert returned_response.uuid == public_query.responses.first().id

    def test_success_with_options(self):
        public_query = public_query_recipe.make(active=True)
        max_answers = 3
        select_question = question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_SELECT,
            max_answers=max_answers,
        )
        options = [
            question_option_recipe.make(question_id=select_question.id, order=index)
            for index in range(5)
        ]
        option_uuids = [opt.id for opt in options]
        answer_data_list = [
            AnswerData(
                question_uuid=select_question.id, options=option_uuids[:max_answers]
            )
        ]
        response_data = ResponseData(
            query_uuid=public_query.id,
            answers=answer_data_list,
        )
        returned_response = services.submit_response(response=response_data)
        response_instance = public_query.responses.first()

        assert returned_response.uuid
        assert all(answer.uuid for answer in returned_response.answers)
        assert returned_response.uuid == response_instance.id

        answer_instance = response_instance.answers.first()
        answer_instance_option_uuids = answer_instance.options.values_list(
            "id", flat=True
        )
        assert len(answer_instance_option_uuids) == max_answers
        assert all(uuid in option_uuids for uuid in answer_instance_option_uuids)
