from uuid import UUID

from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.models import PublicQuery


def get_public_query_by_uuid(uuid: UUID, **kwargs) -> PublicQuery:
    try:
        public_query = PublicQuery.objects.get(id=uuid, **kwargs)
    except PublicQuery.DoesNotExist:
        raise PublicQueryDoesNotExist
    return public_query
