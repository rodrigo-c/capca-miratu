from datetime import datetime
from uuid import UUID

from django.contrib.gis.geos import Point

from apps.public_queries.lib.exceptions import ResponseDoesNotExist
from apps.public_queries.models import Response


def get_response_by_uuid(uuid: UUID) -> Response:
    try:
        response = Response.objects.get(id=uuid)
    except Response.DoesNotExist:
        raise ResponseDoesNotExist
    return response


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
