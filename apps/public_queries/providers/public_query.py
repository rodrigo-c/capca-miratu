from uuid import UUID

from apps.public_queries.models import PublicQuery


def get_public_query_by_uuid(uuid: UUID, **kwargs) -> PublicQuery:
    return PublicQuery.objects.get(id=uuid, **kwargs)


def get_public_query_by_url_code(url_code: str, **kwargs) -> PublicQuery:
    return PublicQuery.objects.get(url_code=url_code, **kwargs)
