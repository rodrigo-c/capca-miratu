from datetime import datetime
from tempfile import NamedTemporaryFile
from uuid import uuid4

import pytest
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.timezone import make_aware

from freezegun import freeze_time

from apps.public_queries import services
from apps.public_queries.lib.constants import (
    PublicQueryResultConstants,
    QuestionConstants,
)
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PublicQueryData,
    QuestionData,
    ResponseData,
)
from apps.public_queries.lib.exceptions import (
    PublicQueryDoesNotExist,
    QuestionDoesNotExist,
)
from apps.public_queries.tests.recipes import (
    public_query_recipe,
    question_option_recipe,
    question_recipe,
)


@pytest.mark.django_db
class TestGetPublicQuery:
    def test_success(self):
        public_query = public_query_recipe.make(active=True)
        public_query_data = services.get_public_query(
            identifier=public_query.id, active=True
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
        public_query_data = services.get_public_query(identifier=str(public_query.id))
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
        public_query_data = services.get_public_query(identifier=public_query.url_code)
        question_data = public_query_data.questions[0]
        option_data = question_data.options[0]
        assert option_data.uuid == option.id
        assert option_data.name == option.name

    def test_does_not_exist_by_uuid(self):
        with pytest.raises(PublicQueryDoesNotExist):
            services.get_public_query(identifier=uuid4())

    def test_does_not_exist_by_url_code(self):
        with pytest.raises(PublicQueryDoesNotExist):
            services.get_public_query(identifier="xs")

    def test_out_of_start_time(self):
        public_query = public_query_recipe.make(
            active=True, start_at=make_aware(datetime(2023, 1, 2))
        )
        with freeze_time("2023-01-01"):
            with pytest.raises(PublicQueryDoesNotExist):
                services.get_public_query(identifier=public_query.id, active=True)

    def test_out_of_end_time(self):
        public_query = public_query_recipe.make(
            active=True, end_at=make_aware(datetime(2023, 1, 1))
        )
        with freeze_time("2023-01-02"):
            with pytest.raises(PublicQueryDoesNotExist):
                services.get_public_query(identifier=public_query.id, active=True)


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

    def test_success_with_point(self):
        public_query = public_query_recipe.make(active=True)
        select_question = question_recipe.make(
            query_id=public_query.id,
            kind=QuestionConstants.KIND_POINT,
        )
        point = Point(1, 1)
        answer_data_list = [AnswerData(question_uuid=select_question.id, point=point)]
        response_data = ResponseData(
            query_uuid=public_query.id,
            answers=answer_data_list,
        )
        returned_response = services.submit_response(response=response_data)
        response_instance = public_query.responses.first()
        assert returned_response.uuid
        assert all(answer.uuid for answer in returned_response.answers)
        assert returned_response.uuid == response_instance.id
        assert response_instance.answers.first().point == point


@pytest.mark.django_db
def test_get_public_query_result(ended_public_query):
    public_query_data = services.get_public_query(identifier=ended_public_query.id)
    result_data = services.get_public_query_result(public_query=public_query_data)
    assert result_data.query == public_query_data
    assert result_data.total_responses == 16
    assert result_data.anonymous_responses == 8
    assert (
        len(result_data.partial_responses)
        == PublicQueryResultConstants.LENGTH_PARTIAL_LIST
    )
    assert len(result_data.answer_results) == 4

    for answer_result in result_data.answer_results:
        if answer_result.question.kind in [
            QuestionConstants.KIND_TEXT,
            QuestionConstants.KIND_IMAGE,
        ]:
            assert (
                len(answer_result.partial_list)
                == PublicQueryResultConstants.LENGTH_PARTIAL_LIST
            )
        if answer_result.question.kind in [
            QuestionConstants.KIND_SELECT,
            QuestionConstants.KIND_POINT,
        ]:
            assert answer_result.partial_list is None

        if answer_result.question.kind == QuestionConstants.KIND_SELECT:
            assert answer_result.options[0].total == 0
            assert answer_result.options[0].percent == 0.0
            assert answer_result.options[1].total == 8
            assert answer_result.options[1].percent == 50.0
            assert answer_result.options[2].total == 8
            assert answer_result.options[2].percent == 50.0
            assert answer_result.options[3].total == 0


@pytest.mark.django_db
class TestGetAnswerResult:
    def test_with_text(self, ended_public_query):
        question = ended_public_query.questions.filter(
            kind=QuestionConstants.KIND_TEXT
        ).first()
        answer_result = services.get_answer_result(
            question_uuid=question.id,
            page_size=5,
        )
        assert answer_result.total == 16
        assert answer_result.question.uuid == question.id
        assert len(answer_result.partial_list) == 5
        assert all(answer_data.text for answer_data in answer_result.partial_list)

    def test_with_image(self, ended_public_query):
        question = ended_public_query.questions.filter(
            kind=QuestionConstants.KIND_IMAGE
        ).first()
        answer_result = services.get_answer_result(
            question_uuid=question.id,
            page_size=5,
        )
        assert answer_result.total == 16
        assert answer_result.question.uuid == question.id
        assert len(answer_result.partial_list) == 5
        assert all(answer_data.image for answer_data in answer_result.partial_list)

    def test_with_select(self, ended_public_query):
        question = ended_public_query.questions.filter(
            kind=QuestionConstants.KIND_SELECT
        ).first()
        with pytest.raises(QuestionDoesNotExist):
            services.get_answer_result(
                question_uuid=question.id,
            )

    def test_with_point(self, ended_public_query):
        question = ended_public_query.questions.filter(
            kind=QuestionConstants.KIND_POINT
        ).first()
        answer_result = services.get_answer_result(
            question_uuid=question.id,
            page_size=5,  # this must not work
        )
        assert answer_result.total == 16
        assert answer_result.question.uuid == question.id
        assert len(answer_result.partial_list) == 16
        assert all(answer_data.point for answer_data in answer_result.partial_list)

    def test_not_found(ended_public_query):
        with pytest.raises(QuestionDoesNotExist):
            services.get_answer_result(
                question_uuid=uuid4(),
            )
