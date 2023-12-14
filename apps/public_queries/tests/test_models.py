import pytest


@pytest.mark.django_db
class TestPublicQuery:
    def test_str(self, public_query):
        assert str(public_query) == f"{public_query.name} ({public_query.url_code})"

    def test_is_active(self, inactive_public_query):
        assert inactive_public_query.is_active is False


@pytest.mark.django_db
class TestQuestion:
    def test_str(self, question):
        assert str(question) == (
            f"[{question.order}][{question.kind}] {question.name[:100]}..."
        )


@pytest.mark.django_db
class TestQuestionOption:
    def test_str(self, question_option):
        assert str(question_option) == f"{question_option.name} [{question_option.id}]"


@pytest.mark.django_db
class TestResponse:
    def test_str(self, response):
        assert str(response) == (
            f"[{str(response.send_at)[:19]}] > {response.query.name[:50]}..."
        )


@pytest.mark.django_db
class TestAnswer:
    def test_str(self, answer):
        assert str(answer) == (f"> {answer.question}")
