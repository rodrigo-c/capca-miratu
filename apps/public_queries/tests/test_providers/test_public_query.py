import pytest

from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.tests.recipes import public_query_recipe


@pytest.mark.django_db
class TestGetPublicQueryByUUID:
    def test_success(self, public_query):
        called_public_query = public_query_providers.get_public_query_by_uuid(
            uuid=public_query.id
        )
        assert called_public_query.id == public_query.id


@pytest.mark.django_db
class TestGetPublicQueryByUrlCode:
    def test_success(self, public_query):
        called_public_query = public_query_providers.get_public_query_by_url_code(
            url_code=public_query.url_code
        )
        assert called_public_query.id == public_query.id


@pytest.mark.django_db
class TestCreatePublicQuery:
    def test_success(self, public_query_data):
        kwargs = {
            **public_query_data.__dict__,
            "user_id": None,
        }
        created_query = public_query_providers.create_public_query(**kwargs)
        assert created_query.id is not None

    def test_with_repeat_url_code(self, public_query_data):
        other_query = public_query_recipe.make()
        kwargs = {
            **public_query_data.__dict__,
            "url_code": other_query.url_code,
            "user_id": None,
        }
        created_query = public_query_providers.create_public_query(**kwargs)
        assert created_query.id is not None
        assert other_query.id != created_query.id
        assert other_query.url_code != created_query.url_code


@pytest.mark.django_db
class TestEmailIsAllowedToPublicQuery:
    def test_is_allowed(self, closed_public_query):
        allowed_email = "allowed@email"
        closed_public_query.allowed_responders.create(email=allowed_email)

        assert (
            public_query_providers.email_is_allowed_to_public_query(
                public_query_uuid=closed_public_query.id, email=allowed_email
            )
            is True
        )

    def test_is_not_allowed(self, closed_public_query):
        assert (
            public_query_providers.email_is_allowed_to_public_query(
                public_query_uuid=closed_public_query.id, email="not.allowed@email"
            )
            is False
        )


@pytest.mark.django_db
def test_get_public_query_list(public_query):
    result = public_query_providers.get_public_query_list()
    assert result[0].id == public_query.id
