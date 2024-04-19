from io import BytesIO
from uuid import UUID

from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.public_queries.domain_logic.auth import CanSubmitPublicQuery
from apps.public_queries.domain_logic.exports import PublicQueryExporter
from apps.public_queries.domain_logic.factories import PublicQueryFactory
from apps.public_queries.domain_logic.results import (
    AnswerResultReturner,
    PublicQueryResultReturner,
    QueryMapResultReturner,
)
from apps.public_queries.domain_logic.returners import PublicQueryReturner
from apps.public_queries.domain_logic.submit import SubmitResponseEngine
from apps.public_queries.lib.constants import (
    PublicQueryConstants,
    PublicQueryResultConstants,
)
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PublicQueryData,
    PublicQueryResultData,
    QueryMapResultData,
    ResponseData,
)
from apps.public_queries.lib.exceptions import (
    PublicQueryCreateError,
    PublicQueryDoesNotExist,
    PublicQueryUpdateError,
    QuestionDoesNotExist,
    ResponseDoesNotExist,
)
from apps.public_queries.models import Question, Response
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import question as question_providers
from apps.public_queries.providers import response as response_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


def get_public_query(
    identifier: UUID | str, active: bool | None = None
) -> PublicQueryData:
    returner = PublicQueryReturner(identifier=identifier, active=active)
    return returner.get()


def get_public_query_list() -> list[PublicQueryData]:
    returner = PublicQueryReturner(identifier="__all__")
    return returner.get()


def create_public_query(
    query_data: PublicQueryData,
    user_id: int | None = None,
) -> PublicQueryData:
    try:
        created_query = PublicQueryFactory(data=query_data).create(user_id=user_id)
    except Exception as error:
        raise PublicQueryCreateError(error)
    return created_query


def update_public_query(query_data: PublicQueryData) -> PublicQueryData:
    try:
        created_query = PublicQueryFactory(data=query_data).update()
    except Exception as error:
        raise PublicQueryUpdateError(error)
    return created_query


def update_question_image(
    question_uuid: UUID, image: InMemoryUploadedFile | None = None
) -> str:
    try:
        image_url = question_providers.update_question_image(
            question_uuid=question_uuid, image=image
        )
    except Question.DoesNotExist:
        raise QuestionDoesNotExist
    return image_url


def delete_public_query(uuid: str | UUID) -> bool:
    obj_deleted, detail = public_query_providers.delete_public_query(uuid=uuid)
    return detail.get("public_queries.PublicQuery") == 1


def get_submit_public_query(
    identifier: UUID | str,
    email: str | None = None,
    secret_key: str | None = None,
) -> PublicQueryData:
    public_query = PublicQueryReturner(identifier=identifier, active=True).get()
    if public_query.kind == PublicQueryConstants.KIND_OPEN:
        return public_query
    if (
        public_query.kind == PublicQueryConstants.KIND_CLOSED
        and (email and secret_key)
        and CanSubmitPublicQuery(
            query_identifier=identifier,
            responder_email=email,
            secret_key=secret_key,
        ).is_valid()
    ):
        return public_query
    raise PublicQueryDoesNotExist


def get_response_by_uuid(uuid: UUID) -> ResponseData:
    try:
        uuid = UUID(uuid) if not isinstance(uuid, UUID) else uuid
        instance = response_providers.get_response_by_uuid(uuid=uuid)
    except (ValueError, Response.DoesNotExist):
        raise ResponseDoesNotExist

    public_query_data = get_public_query(identifier=instance.query_id)
    return build_dataclass_from_model_instance(
        klass=ResponseData,
        instance=instance,
        uuid=instance.id,
        query_uuid=instance.query_id,
        query_data=public_query_data,
    )


def submit_response(
    response: ResponseData, public_query: PublicQueryData | None = None
) -> ResponseData:
    engine = SubmitResponseEngine(response=response, public_query=public_query)
    return engine.submit()


def get_public_query_result(public_query: PublicQueryData) -> PublicQueryResultData:
    returner = PublicQueryResultReturner(public_query=public_query)
    return returner.get()


def get_public_query_response_result(
    public_query: PublicQueryData,
    page_num: int | None = None,
    page_size: int = PublicQueryResultConstants.DEFAULT_PAGE_SIZE,
) -> PublicQueryResultData:
    returner = PublicQueryResultReturner(
        public_query=public_query,
        page_size=page_size,
    )
    return returner.get_responses(page_num=page_num)


def get_public_query_responses_data(identifier: str | UUID) -> dict:
    return PublicQueryReturner(identifier=identifier).get_responses_data()


def get_answer_result(
    question_uuid: UUID,
    page_num: int | None = None,
    page_size: int | None = None,
) -> list[AnswerData]:
    returner = AnswerResultReturner(
        question_uuid=question_uuid,
        page_size=page_size,
    )
    return returner.get(page_num=page_num)


def get_public_query_map_result(identifier: UUID | str) -> QueryMapResultData:
    returner = QueryMapResultReturner(
        identifier=identifier,
    )
    return returner.get()


def can_submit_public_query(
    query_identifier: UUID | str,
    email: str | None = None,
    rut: str | None = None,
    secret_key: str | None = None,
) -> None:
    return CanSubmitPublicQuery(
        query_identifier=query_identifier,
        responder_email=email,
        responder_rut=rut,
        secret_key=secret_key,
    ).validate()


def get_public_query_share_document(
    public_query: PublicQueryData, host: str | None = None
) -> BytesIO:
    return PublicQueryExporter(public_query=public_query, host=host).get_share_pdf()
