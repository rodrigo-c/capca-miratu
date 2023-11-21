from uuid import UUID

from django.utils import timezone

from apps.public_queries.lib.dataclasses import PublicQueryData
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.providers import public_query as public_query_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


def get_public_query_by_uuid(uuid: UUID) -> PublicQueryData:
    public_query = public_query_providers.get_public_query_by_uuid(uuid=uuid)
    return build_dataclass_from_model_instance(
        klass=PublicQueryData,
        instance=public_query,
        uuid=public_query.id,
        image=public_query.image.url if public_query.image else None,
    )


def get_active_public_query_by_uuid(uuid: UUID) -> PublicQueryData:
    now = timezone.now()
    public_query = public_query_providers.get_public_query_by_uuid(
        uuid=uuid, active=True
    )
    is_after_start = public_query.start_at is None or public_query.start_at < now
    is_before_end = public_query.end_at is None or public_query.end_at > now
    if is_after_start and is_before_end:
        return build_dataclass_from_model_instance(
            klass=PublicQueryData,
            instance=public_query,
            uuid=public_query.id,
            image=public_query.image.url if public_query.image else None,
        )
    raise PublicQueryDoesNotExist
