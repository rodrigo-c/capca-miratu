from uuid import UUID

from apps.public_queries.models import PublicQuery
from apps.utils.random import get_random_url_code


def get_public_query_list() -> list[PublicQuery]:
    return PublicQuery.objects.all()


def get_public_query_by_uuid(uuid: UUID, **kwargs) -> PublicQuery:
    return PublicQuery.objects.get(id=uuid, **kwargs)


def get_public_query_by_url_code(url_code: str, **kwargs) -> PublicQuery:
    return PublicQuery.objects.get(url_code=url_code, **kwargs)


def email_is_allowed_to_public_query(public_query_uuid: UUID, email: str) -> bool:
    return PublicQuery.objects.filter(
        id=public_query_uuid, allowed_responders__email=email
    ).exists()


def create_public_query(name, kind, user_id, **kwargs) -> PublicQuery:
    url_code = None
    while url_code is None:
        if "url_code" in kwargs:
            url_code = kwargs["url_code"]
            kwargs.pop("url_code")
        else:
            url_code = get_random_url_code()
        if PublicQuery.objects.filter(url_code=url_code).exists():
            url_code = None

    other_fields = [
        "description",
        "start_at",
        "end_at",
        "active",
        "max_responses",
        "auth_rut",
        "auth_email",
    ]
    other_values = {field: kwargs[field] for field in other_fields if field in kwargs}
    return PublicQuery.objects.create(
        name=name, kind=kind, created_by_id=user_id, **other_values
    )
