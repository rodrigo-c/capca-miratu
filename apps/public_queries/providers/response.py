from datetime import datetime
from uuid import UUID

from django.contrib.gis.geos import Point

from apps.public_queries.models import Response


def get_response_by_uuid(uuid: UUID, **kwargs) -> Response:
    return Response.objects.get(id=uuid, **kwargs)


def create_response(
    query_uuid: str | UUID,
    send_at: datetime,
    location: Point | None = None,
    email: str | None = None,
    rut: str | None = None,
) -> Response:
    return Response.objects.create(
        query_id=query_uuid, send_at=send_at, location=location, email=email, rut=rut
    )


def get_total_responses_by_query_uuid(query_uuid: UUID) -> int:
    return Response.objects.filter(query_id=query_uuid).count()


def get_anonymous_responses_by_query_uuid(query_uuid: UUID) -> int:
    return Response.objects.filter(
        query_id=query_uuid, email__isnull=True, rut__isnull=True
    ).count()


def get_responses_by_query_uuid(query_uuid: UUID) -> list[Response]:
    return Response.objects.filter(query_id=query_uuid)


def count_responses_by_query_and_rut(query_uuid: UUID, rut: str) -> int:
    return Response.objects.filter(query_id=query_uuid, rut=rut).count()


def count_responses_by_query_and_email(query_uuid: UUID, email: str) -> int:
    return Response.objects.filter(query_id=query_uuid, email=email).count()


def update_response_visibility(response_uuid: UUID, visible: bool) -> bool:
    response = Response.objects.get(id=response_uuid)
    response.visible = visible
    response.save(update_fields=["visible"])
    return visible
