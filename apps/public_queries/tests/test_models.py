import pytest


@pytest.mark.django_db
class TestPublicQuery:
    def test_str(self, public_query):
        class_name = public_query.__class__.__name__
        assert (
            str(public_query)
            == f"{class_name}: {public_query.name} ({public_query.id})"
        )


@pytest.mark.django_db
class TestQuestion:
    def test_str(self, question):
        class_name = question.__class__.__name__
        assert str(question) == f"{class_name}: {question.name} ({question.id})"
