import pytest

from apps.public_queries import services
from apps.public_queries.lib.dataclasses import PublicQueryData


@pytest.mark.django_db
def test_get_public_query_by_uuid(public_query):
    public_query_data = services.get_public_query_by_uuid(uuid=public_query.id)
    assert isinstance(public_query_data, PublicQueryData)
    assert public_query_data.uuid == public_query.id
    assert public_query_data.active is False
    assert isinstance(public_query_data.name, str)
