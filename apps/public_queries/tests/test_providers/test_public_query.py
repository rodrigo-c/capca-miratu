import pytest

from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.providers import public_query as public_query_providers


@pytest.mark.django_db
class TestGetPublicQueryByUUID:
    def test_success(self, public_query):
        called_public_query = public_query_providers.get_public_query_by_uuid(
            uuid=public_query.id
        )
        assert called_public_query.id == public_query.id

    def test_not_exist(self):
        with pytest.raises(PublicQueryDoesNotExist):
            public_query_providers.get_public_query_by_uuid(uuid=0)
