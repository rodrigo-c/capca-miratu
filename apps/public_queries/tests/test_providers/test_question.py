import pytest

from apps.public_queries.providers import question as question_providers


@pytest.mark.django_db
class TestGetQuestionsByPublicQuerUUID:
    def test_success(self, question):
        queryset = question_providers.get_questions_by_public_query_uuid(
            uuid=question.query_id
        )
        assert queryset.first().id == question.id


@pytest.mark.django_db
def test_get_question_by_uuid(question):
    returned_instance = question_providers.get_question_by_uuid(uuid=question.id)
    assert returned_instance.id == question.id


@pytest.mark.django_db
def test_bulk_create_questions(public_query):
    name = "eman"
    question_data = {
        "name": name,
        "kind": "OPEN",
        "required": True,
        "query_uuid": public_query.id,
    }
    data_list = [question_data]
    returned_questions = question_providers.bulk_create_questions(data_list=data_list)
    assert returned_questions[0].name == name


@pytest.mark.django_db
def test_bulk_update_questions(question):
    name = "eman"
    question_data = {
        "name": name,
        "query_uuid": question.query_id,
        "uuid": question.id,
    }
    data_list = [question_data]
    assert question_providers.bulk_update_questions(data_list=data_list) == len(
        data_list
    )
    question.refresh_from_db()
    assert question.name == name


@pytest.mark.django_db
def test_update_question_image(question, uploaded_image):
    assert not question.image
    returned_url = question_providers.update_question_image(
        question_uuid=question.id, image=uploaded_image
    )
    question.refresh_from_db()
    assert returned_url == question.image.url
