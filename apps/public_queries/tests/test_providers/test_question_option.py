import pytest

from apps.public_queries.providers import question_option as question_option_providers


@pytest.mark.django_db
def test_get_question_options_by_query_uuid(question_option):
    returned_question_options = (
        question_option_providers.get_question_options_by_query_uuid(
            query_uuid=question_option.question.query_id
        )
    )
    assert returned_question_options[0].id == question_option.id


@pytest.mark.django_db
def test_bulk_create_question_options(question):
    name = "eman"
    question_option_data = {"name": name, "question_uuid": question.id}
    data_list = [question_option_data]
    returned_question_options = question_option_providers.bulk_create_question_options(
        data_list=data_list
    )
    assert returned_question_options[0].id
    assert returned_question_options[0].name == name
    assert returned_question_options[0].question_id == question.id


@pytest.mark.django_db
def test_bulk_update_question_options(question_option):
    name = "eman"
    question_option_data = {
        "name": name,
        "question_uuid": question_option.question_id,
        "uuid": question_option.id,
    }
    data_list = [question_option_data]
    assert question_option_providers.bulk_update_question_options(
        data_list=data_list
    ) == len(data_list)
    question_option.refresh_from_db()
    assert question_option.name == name


@pytest.mark.django_db
def test_update_question_option_image(question_option, uploaded_image):
    assert not question_option.image
    returned_url = question_option_providers.update_question_option_image(
        option_uuid=question_option.id, image=uploaded_image
    )
    question_option.refresh_from_db()
    assert returned_url == question_option.image.url
