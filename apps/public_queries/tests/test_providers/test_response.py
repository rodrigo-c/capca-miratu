import pytest
from django.utils import timezone

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


@pytest.mark.django_db
def test_get_total_responses_by_query_uuid(ended_public_query):
    assert (
        response_providers.get_total_responses_by_query_uuid(
            query_uuid=ended_public_query.id
        )
    ) == 16


@pytest.mark.django_db
def test_get_anonymous_responses_by_query_uuid(ended_public_query):
    assert (
        response_providers.get_anonymous_responses_by_query_uuid(
            query_uuid=ended_public_query.id
        )
    ) == 8


@pytest.mark.django_db
def test_get_responses_by_query_uuid(response):
    returned_instances = response_providers.get_responses_by_query_uuid(
        query_uuid=response.query_id
    )
    assert response.id == returned_instances[0].id


@pytest.mark.django_db
def test_count_responses_by_query_and_rut(response):
    assert (
        response_providers.count_responses_by_query_and_rut(
            query_uuid=response.query_id, rut=response.rut
        )
        == 1
    )


@pytest.mark.django_db
def test_count_responses_by_query_and_email(response):
    assert (
        response_providers.count_responses_by_query_and_email(
            query_uuid=response.query_id, email=response.email
        )
        == 1
    )


@pytest.mark.django_db
def test_update_response_visibility(response):
    assert response.visible is True
    assert (
        response_providers.update_response_visibility(
            response_uuid=response.id, visible=False
        )
        is False
    )
    response.refresh_from_db()
    assert response.visible is False
    assert (
        response_providers.update_response_visibility(
            response_uuid=response.id, visible=True
        )
        is True
    )
    response.refresh_from_db()
    assert response.visible is True
