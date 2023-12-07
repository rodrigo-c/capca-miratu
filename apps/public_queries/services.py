from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PublicQueryData,
    QuestionData,
    QuestionOptionData,
    ResponseData,
)
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.models import Answer, PublicQuery, Question, Response
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import question as question_providers
from apps.public_queries.providers import response as response_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


class PublicQueryReturner:
    def __init__(self, identifier: UUID | str, active: bool | None = None):
        kwargs = {} if active is None else {"active": active}

        if len(str(identifier)) <= getattr(settings, "MAXIMUM_URL_CHARS", 5):
            public_query = self._get_obj_by_url_code(url_code=identifier, **kwargs)
        else:
            public_query = self._get_obj_by_uuid(uuid=identifier, **kwargs)
        now = timezone.now()
        is_after_start = public_query.start_at is None or public_query.start_at < now
        is_before_end = public_query.end_at is None or public_query.end_at > now
        if active and (not is_after_start or not is_before_end):
            raise PublicQueryDoesNotExist
        self.public_query = public_query

    def _get_obj_by_url_code(self, url_code: str, **kwargs) -> PublicQuery:
        try:
            public_query = public_query_providers.get_public_query_by_url_code(
                url_code=url_code, **kwargs
            )
        except PublicQuery.DoesNotExist:
            raise PublicQueryDoesNotExist
        return public_query

    def _get_obj_by_uuid(self, uuid: UUID, **kwargs) -> PublicQuery:
        try:
            uuid = UUID(uuid) if not isinstance(uuid, UUID) else uuid
            public_query = public_query_providers.get_public_query_by_uuid(
                uuid=uuid, **kwargs
            )
        except (ValueError, PublicQuery.DoesNotExist):
            raise PublicQueryDoesNotExist
        return public_query

    def get(self) -> PublicQueryData:
        question_queryset = question_providers.get_questions_by_public_query_uuid(
            uuid=self.public_query.id
        )
        questions = [
            build_dataclass_from_model_instance(
                klass=QuestionData,
                instance=question,
                uuid=question.id,
                query_uuid=self.public_query.id,
                index=index,
                options=self._get_options_data(question=question),
            )
            for index, question in enumerate(question_queryset)
        ]
        return build_dataclass_from_model_instance(
            klass=PublicQueryData,
            instance=self.public_query,
            uuid=self.public_query.id,
            image=self.public_query.image.url if self.public_query.image else None,
            questions=questions or None,
        )

    def _get_options_data(self, question: Question) -> list[QuestionOptionData]:
        if question.kind == QuestionConstants.KIND_SELECT:
            return [
                build_dataclass_from_model_instance(
                    klass=QuestionOptionData,
                    instance=option,
                    uuid=option.id,
                    question_uuid=option.question_id,
                )
                # TODO: use one query select for all questions instead
                for option in question.options.all()
            ]


def get_public_query(
    identifier: UUID | str, active: bool | None = None
) -> PublicQueryData:
    returner = PublicQueryReturner(identifier=identifier, active=active)
    return returner.get()


def get_public_query_by_uuid(uuid: UUID) -> PublicQueryData:
    public_query = public_query_providers.get_public_query_by_uuid(uuid=uuid)
    return build_dataclass_from_model_instance(
        klass=PublicQueryData,
        instance=public_query,
        uuid=public_query.id,
        image=public_query.image.url if public_query.image else None,
    )


def _get_options_data(question: Question) -> list[QuestionOptionData]:
    if question.kind == QuestionConstants.KIND_SELECT:
        return [
            build_dataclass_from_model_instance(
                klass=QuestionOptionData,
                instance=option,
                uuid=option.id,
                question_uuid=option.question_id,
            )
            # TODO: use one query select for all questions instead
            for option in question.options.all()
        ]


def _return_public_query_data_if_is_active(
    public_query: PublicQuery,
) -> PublicQueryData:
    now = timezone.now()
    is_after_start = public_query.start_at is None or public_query.start_at < now
    is_before_end = public_query.end_at is None or public_query.end_at > now
    if is_after_start and is_before_end:
        question_queryset = question_providers.get_questions_by_public_query_uuid(
            uuid=public_query.id
        )
        questions = [
            build_dataclass_from_model_instance(
                klass=QuestionData,
                instance=question,
                uuid=question.id,
                query_uuid=public_query.id,
                index=index,
                options=_get_options_data(question=question),
            )
            for index, question in enumerate(question_queryset)
        ]
        return build_dataclass_from_model_instance(
            klass=PublicQueryData,
            instance=public_query,
            uuid=public_query.id,
            image=public_query.image.url if public_query.image else None,
            questions=questions or None,
        )
    raise PublicQueryDoesNotExist


def get_active_public_query_by_uuid(uuid: UUID) -> PublicQueryData:
    public_query = public_query_providers.get_public_query_by_uuid(
        uuid=uuid, active=True
    )
    return _return_public_query_data_if_is_active(public_query=public_query)


def get_active_public_query_by_url_code(url_code: str) -> PublicQueryData:
    public_query = public_query_providers.get_public_query_by_url_code(
        url_code=url_code, active=True
    )
    return _return_public_query_data_if_is_active(public_query=public_query)


def get_response_by_uuid(uuid: UUID) -> ResponseData:
    instance = response_providers.get_response_by_uuid(uuid=uuid)
    public_query_data = get_active_public_query_by_uuid(uuid=instance.query_id)
    return build_dataclass_from_model_instance(
        klass=ResponseData,
        instance=instance,
        uuid=instance.id,
        query_uuid=instance.query_id,
        query_data=public_query_data,
    )


class SubmitResponseEngine:
    def __init__(
        self, response: ResponseData, public_query: PublicQueryData | None = None
    ):
        if not public_query:
            public_query = get_active_public_query_by_uuid(uuid=response.query_uuid)

        self.question_map = self._get_question_map(
            response=response, public_query=public_query
        )
        self.response = response
        self.public_query = public_query

    def _get_question_map(
        self, response: ResponseData, public_query: PublicQueryData
    ) -> None:
        question_map = {question.uuid: question for question in public_query.questions}
        question_uuids_with_answers = [
            answer.question_uuid for answer in response.answers
        ]
        assert response.query_uuid == public_query.uuid
        assert all(answer.question_uuid in question_map for answer in response.answers)
        assert all(
            question.uuid in question_uuids_with_answers
            for question in public_query.questions
            if question.required
        )
        return question_map

    def submit(self) -> ResponseData:
        with transaction.atomic():
            response_instance = self._create_response()
            answer_instances = self._create_answers(response_instance=response_instance)
        return self._build_response_data(
            response_instance=response_instance, answer_instances=answer_instances
        )

    def _create_response(self) -> Response:
        now = timezone.now()
        return response_providers.create_response(
            query_uuid=self.public_query.uuid,
            send_at=now,
            email=self.response.email,
            rut=self.response.rut,
            location=self.response.location,
        )

    def _create_answers(self, response_instance: Response) -> list[Answer]:
        answer_data_list = []
        options_map = {}
        for answer in self.response.answers:
            question = self.question_map[answer.question_uuid]
            answer_data = {
                "question_id": answer.question_uuid,
                "response_id": response_instance.id,
            }
            if question.kind == QuestionConstants.KIND_TEXT:
                answer_data["text"] = answer.text
            elif question.kind == QuestionConstants.KIND_IMAGE:
                answer_data["image"] = answer.image
            elif question.kind == QuestionConstants.KIND_SELECT:
                assert question.max_answers >= len(answer.options)
                options_map[answer.question_uuid] = answer
            elif question.kind == QuestionConstants.KIND_POINT:
                answer_data["point"] = answer.point
            answer_data_list.append(answer_data)
        instances = answer_providers.bulk_create_answers(answers=answer_data_list)
        return self._add_answer_options(instances=instances, options_map=options_map)

    def _add_answer_options(
        self, instances: list[Answer], options_map: dict[UUID, AnswerData]
    ) -> list[Answer]:
        for answer in instances:
            options = None
            if answer.question_id in options_map:
                options = options_map[answer.question_id].options
                answer.options.add(*options)
            answer._cached_options = options
        return instances

    def _build_response_data(
        self, response_instance: Response, answer_instances: list[Answer]
    ) -> ResponseData:
        answers = self._build_answer_data_list(instances=answer_instances)
        return build_dataclass_from_model_instance(
            klass=ResponseData,
            instance=response_instance,
            uuid=response_instance.id,
            query_uuid=response_instance.query_id,
            answers=answers,
            query_data=self.public_query,
        )

    def _build_answer_data_list(self, instances: list[Answer]) -> list[AnswerData]:
        answers = [
            build_dataclass_from_model_instance(
                klass=AnswerData,
                instance=instance,
                uuid=instance.id,
                response_uuid=instance.response_id,
                question_uuid=instance.question_id,
                image=instance.image.url if instance.image else None,
                options=instance._cached_options,
            )
            for instance in instances
        ]
        return answers


def submit_response(
    response: ResponseData, public_query: PublicQueryData | None = None
) -> ResponseData:
    engine = SubmitResponseEngine(response=response, public_query=public_query)
    return engine.submit()
