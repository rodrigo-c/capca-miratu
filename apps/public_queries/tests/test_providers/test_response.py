import pytest
from django.utils import timezone

from apps.public_queries.lib.exceptions import ResponseDoesNotExist
from apps.public_queries.models import Response
from apps.public_queries.providers import response as response_providers


@pytest.mark.django_db
def test_create_response(public_query):
    returned_instance = response_providers.create_response(
        query_uuid=public_query.id,
        send_at=timezone.now(),
        email="fake@email.com",
        rut="1000000-1",
    )
    assert returned_instance.id
    assert isinstance(returned_instance, Response)
    assert returned_instance.query_id == public_query.id


@pytest.mark.django_db
def test_get_response_by_uuid(response):
    returned_instance = response_providers.get_response_by_uuid(uuid=response.id)
    assert response.id == returned_instance.id
    with pytest.raises(ResponseDoesNotExist):
        response_providers.get_response_by_uuid(uuid=0)
