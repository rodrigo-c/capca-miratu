from datetime import datetime
from uuid import UUID

from django.contrib.gis.geos import Point

from apps.public_queries.models import Response


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
