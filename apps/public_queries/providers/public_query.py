from uuid import UUID

from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.models import PublicQuery


def get_public_query_by_uuid(uuid: UUID, **kwargs) -> PublicQuery:
    try:
        public_query = PublicQuery.objects.get(id=uuid, **kwargs)
    except PublicQuery.DoesNotExist:
        raise PublicQueryDoesNotExist
    return public_query


def get_public_query_by_url_code(url_code: str, **kwargs) -> PublicQuery:
    try:
        public_query = PublicQuery.objects.get(url_code=url_code, **kwargs)
    except PublicQuery.DoesNotExist:
        raise PublicQueryDoesNotExist
    return public_query
