from uuid import UUID

from apps.public_queries.lib.dataclasses import PublicQueryData
from apps.public_queries.providers import public_query as public_query_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


def get_public_query_by_uuid(uuid: UUID) -> PublicQueryData:
    public_query = public_query_providers.get_public_query_by_uuid(uuid=uuid)
    return build_dataclass_from_model_instance(
        klass=PublicQueryData, instance=public_query, uuid=public_query.id
    )
