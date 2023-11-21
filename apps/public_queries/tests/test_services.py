from datetime import datetime

import pytest
from django.utils.timezone import make_aware

from freezegun import freeze_time

from apps.public_queries import services
from apps.public_queries.lib.dataclasses import PublicQueryData
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.tests.recipes import public_query_recipe


@pytest.mark.django_db
def test_get_public_query_by_uuid(public_query):
    public_query_data = services.get_public_query_by_uuid(uuid=public_query.id)
    assert isinstance(public_query_data, PublicQueryData)
    assert public_query_data.uuid == public_query.id
    assert public_query_data.active is False
    assert isinstance(public_query_data.name, str)
    assert public_query_data.image is None


@pytest.mark.django_db
class TestGetActivePublicQueryByUUID:
    def test_success(self):
        public_query = public_query_recipe.make(active=True)
        public_query_data = services.get_active_public_query_by_uuid(
            uuid=public_query.id
        )
        assert isinstance(public_query_data, PublicQueryData)
        assert public_query_data.uuid == public_query.id
        assert isinstance(public_query_data.name, str)
        assert public_query_data.image is None

    def test_out_of_start_time(self):
        public_query = public_query_recipe.make(
            active=True, start_at=make_aware(datetime(2023, 1, 2))
        )
        with freeze_time("2023-01-01"):
            with pytest.raises(PublicQueryDoesNotExist):
                services.get_active_public_query_by_uuid(uuid=public_query.id)

    def test_out_of_end_time(self):
        public_query = public_query_recipe.make(
            active=True, end_at=make_aware(datetime(2023, 1, 1))
        )
        with freeze_time("2023-01-02"):
            with pytest.raises(PublicQueryDoesNotExist):
                services.get_active_public_query_by_uuid(uuid=public_query.id)
