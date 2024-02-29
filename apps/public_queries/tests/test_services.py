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
    AuthConstants,
    PublicQueryConstants,
    PublicQueryResultConstants,
    QueryMapResultConstants,
    QuestionConstants,
)
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PublicQueryData,
    QuestionData,
    ResponseData,
)
from apps.public_queries.lib.exceptions import (
    CantSubmitPublicQueryError,
    PublicQueryCreateError,
    PublicQueryDoesNotExist,
    PublicQueryUpdateError,
    QuestionDoesNotExist,
)
from apps.public_queries.tests.recipes import (
    public_query_recipe,
    question_option_recipe,
    question_recipe,
    response_recipe,
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
class TestGetSubmitPublicQuery:
    def test_success_with_open(self):
        public_query = public_query_recipe.make(active=True)
        public_query_data = services.get_submit_public_query(identifier=public_query.id)
        assert public_query_data.uuid == public_query.id

    def test_success_with_closed(self, make_closed_public_query):
        valid_email = "valid@ema.il"
        public_query = make_closed_public_query(emails=[valid_email])
        secret_key = public_query.allowedresponder_set.first().email_code
        public_query_data = services.get_submit_public_query(
            identifier=public_query.id, email=valid_email, secret_key=secret_key
        )
        assert public_query_data.uuid == public_query.id

    def test_not_found_with_closed(self, make_closed_public_query):
        invalid_email = "invalid@ema.il"
        public_query = make_closed_public_query(emails=[invalid_email])
        secret_key = public_query.allowedresponder_set.first().email_code[:-2]
        with pytest.raises(PublicQueryDoesNotExist):
            services.get_submit_public_query(
                identifier=public_query.id, email=invalid_email, secret_key=secret_key
            )


@pytest.mark.django_db
def test_get_response_by_uuid(response):
    response_data = services.get_response_by_uuid(uuid=response.id)
    assert response_data.uuid == response.id
    assert isinstance(response_data, ResponseData)
    assert isinstance(response_data.query_data, PublicQueryData)


@pytest.mark.django_db
def test_get_public_query_responses_data(ended_public_query):
    question_recipe.make(query_id=ended_public_query.id, required=False)
    responses_data = services.get_public_query_responses_data(
        identifier=ended_public_query.url_code
    )
    assert responses_data["query"]["uuid"] == str(ended_public_query.id)
    assert len(responses_data["dataset"]) == 16


@pytest.mark.django_db
class TestCreatePublicQuery:
    def test_success(self, public_query_data):
        created_query = services.create_public_query(query_data=public_query_data)
        assert created_query.uuid is not None
        assert all(question.uuid is not None for question in created_query.questions)
        assert created_query.questions[2].kind == QuestionConstants.KIND_SELECT
        assert all(
            option.uuid is not None for option in created_query.questions[2].options
        )

    def test_error(self):
        with pytest.raises(PublicQueryCreateError) as error:
            services.create_public_query(query_data={})
        assert error.value.__class__ == PublicQueryCreateError


@pytest.mark.django_db
class TestUpdatePublicQuery:
    def test_success(self, ended_public_query):
        public_query_data = services.get_public_query(identifier=ended_public_query.id)
        basic_data_modified = {
            "name": "public_query_modified",
            "description": "_modified",
            "active": not public_query_data.active,
            "max_responses": 10,
            "auth_rut": PublicQueryConstants.AUTH_REQUIRED,
            "auth_email": PublicQueryConstants.AUTH_REQUIRED,
        }
        for field, value in basic_data_modified.items():
            setattr(public_query_data, field, value)

        removed_question_uuid = public_query_data.questions[0].uuid
        new_question_name = "new_question_name"
        public_query_data.questions[0].uuid = None
        public_query_data.questions[0].name = new_question_name
        for index, question in enumerate(public_query_data.questions):
            question.order = index

        new_name_question_select = "new select question"
        public_query_data.questions[2].name = new_name_question_select
        public_query_data.questions[2].options[-1].name = new_name_question_select
        removed_question_option_uuid = public_query_data.questions[2].options[0].uuid
        public_query_data.questions[2].options[0].uuid = None
        public_query_data.questions[2].options[0].name = new_name_question_select
        for index, option in enumerate(public_query_data.questions[2].options):
            option.order = index

        services.update_public_query(query_data=public_query_data)

        ended_public_query.refresh_from_db()
        for field, value in basic_data_modified.items():
            assert getattr(ended_public_query, field) == value

        questions = list(ended_public_query.questions.all())
        assert questions[0].name == new_question_name
        assert questions[0].id != removed_question_uuid
        assert questions[1].id == public_query_data.questions[1].uuid
        assert questions[-1].id == public_query_data.questions[-1].uuid
        assert questions[2].id == public_query_data.questions[2].uuid
        assert questions[2].name == new_name_question_select
        options = list(questions[2].options.all())
        assert options[-1].id == public_query_data.questions[2].options[-1].uuid
        assert options[-1].name == new_name_question_select
        assert options[0].name == new_name_question_select
        assert options[0].id != removed_question_option_uuid

    def test_error(self):
        with pytest.raises(PublicQueryUpdateError):
            services.update_public_query(query_data={})


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
def test_get_public_query_list(public_query):
    result = services.get_public_query_list()
    assert result[0].uuid == public_query.id


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
def test_get_public_query_response_result(ended_public_query):
    public_query_data = services.get_public_query(identifier=ended_public_query.id)
    public_query_result = services.get_public_query_response_result(
        public_query=public_query_data,
        page_size=2,
    )
    assert public_query_result.page_num == 1
    assert public_query_result.num_pages == 8
    assert len(public_query_result.partial_responses) == 2


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


@pytest.mark.django_db
class TestGetPublicQueryMapResult:
    def test_with_point_question(self, ended_public_query):
        public_query_result = services.get_public_query_map_result(
            identifier=ended_public_query.id
        )
        point_question = ended_public_query.questions.filter(
            kind=QuestionConstants.KIND_POINT
        ).first()
        assert public_query_result.query.uuid == ended_public_query.id
        assert len(public_query_result.point_list) == 16
        for point_data in public_query_result.point_list:
            assert point_data.related_label == point_question.name

    def test_with_location(self, ended_public_query):
        ended_public_query.questions.filter(kind=QuestionConstants.KIND_POINT).delete()
        public_query_result = services.get_public_query_map_result(
            identifier=ended_public_query.id
        )
        assert public_query_result.query.uuid == ended_public_query.id
        assert len(public_query_result.point_list) == 16
        for point_data in public_query_result.point_list:
            assert point_data.related_label == QueryMapResultConstants.LOCATION


@pytest.mark.django_db
class TestCanSubmitPublicQuery:
    def test_email_required(self):
        public_query = public_query_recipe.make(
            auth_email=PublicQueryConstants.AUTH_REQUIRED
        )
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id,
            )
        assert error.value.data["email"] == AuthConstants.EMAIL_REQUIRED

    def test_rut_required(self):
        public_query = public_query_recipe.make(
            auth_rut=PublicQueryConstants.AUTH_REQUIRED
        )
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id,
            )
        assert error.value.data["rut"] == AuthConstants.RUT_REQUIRED

    def test_with_invalid_email(self):
        public_query = public_query_recipe.make(
            auth_email=PublicQueryConstants.AUTH_REQUIRED
        )
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id, email="invalid.email"
            )
        assert error.value.data["email"] == AuthConstants.EMAIL_INVALID

    def test_with_not_allowed_email(self):
        public_query = public_query_recipe.make(kind=PublicQueryConstants.KIND_CLOSED)
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id, email="not.allowed@email.com"
            )
        assert error.value.data["email"] == AuthConstants.EMAIL_NOT_ALLOWED

    def test_with_email_max_responses(self):
        public_query = public_query_recipe.make(
            max_responses=1,
            auth_email=PublicQueryConstants.AUTH_REQUIRED,
        )
        repeated_email = "reapeated@email.com"
        response_recipe.make(query_id=public_query.id, email=repeated_email)
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id, email=repeated_email
            )
        assert error.value.data["email"] == AuthConstants.EMAIL_MAX_RESPONSES

    def test_with_invalid_rut(self):
        public_query = public_query_recipe.make(
            auth_rut=PublicQueryConstants.AUTH_REQUIRED
        )
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id, rut="10.000.000-1"
            )
        assert error.value.data["rut"] == AuthConstants.RUT_INVALID

    def test_with_rut_max_responses(self):
        public_query = public_query_recipe.make(
            max_responses=1, auth_rut=PublicQueryConstants.AUTH_REQUIRED
        )
        repeated_rut = "10000000-8"
        response_recipe.make(query_id=public_query.id, rut=repeated_rut)
        with pytest.raises(CantSubmitPublicQueryError) as error:
            services.can_submit_public_query(
                query_identifier=public_query.id, rut=repeated_rut
            )
        assert error.value.data["rut"] == AuthConstants.RUT_MAX_RESPONSES

    def test_success(self):
        public_query = public_query_recipe.make(
            max_responses=2, auth_rut=PublicQueryConstants.AUTH_REQUIRED
        )
        repeated_rut = "10000000-8"
        response_recipe.make(query_id=public_query.id, rut=repeated_rut)
        assert (
            services.can_submit_public_query(
                query_identifier=public_query.id, rut=repeated_rut
            )
            is None
        )
