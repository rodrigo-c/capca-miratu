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
