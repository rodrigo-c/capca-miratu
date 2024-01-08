from uuid import UUID

from apps.public_queries.models import AllowedResponder


def allowed_responder_exists(query_uuid: UUID, email: str, email_code: str) -> bool:
    return AllowedResponder.objects.filter(
        query_id=query_uuid, responder__email=email, email_code=email_code
    ).exists()
