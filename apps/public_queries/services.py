from uuid import UUID

from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from apps.public_queries.lib.constants import (
    PublicQueryResultConstants,
    QuestionConstants,
)
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    AnswerResultData,
    OptionResultData,
    PublicQueryData,
    PublicQueryResultData,
    QuestionData,
    QuestionOptionData,
    ResponseData,
)
from apps.public_queries.lib.exceptions import (
    PublicQueryDoesNotExist,
    QuestionDoesNotExist,
    ResponseDoesNotExist,
)
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
        if active and not public_query.is_active:
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


class ServiceBase:
    def _build_answer_data_list(self, instances: list[Answer]) -> list[AnswerData]:
        answers = [
            build_dataclass_from_model_instance(
                klass=AnswerData,
                instance=instance,
                uuid=instance.id,
                response_uuid=instance.response_id,
                question_uuid=instance.question_id,
                image=instance.image.url if instance.image else None,
                options=getattr(instance, "_cached_options", None),
            )
            for instance in instances
        ]
        return answers


class SubmitResponseEngine(ServiceBase):
    def __init__(
        self, response: ResponseData, public_query: PublicQueryData | None = None
    ):
        if not public_query:
            public_query = get_public_query(identifier=response.query_uuid)

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
            empty = True
            if question.kind == QuestionConstants.KIND_TEXT:
                answer_data["text"] = answer.text
                empty = False if answer.text else True
            elif question.kind == QuestionConstants.KIND_IMAGE:
                answer_data["image"] = answer.image
                empty = False if answer.image else True
            elif question.kind == QuestionConstants.KIND_SELECT:
                assert question.max_answers >= len(answer.options)
                options_map[answer.question_uuid] = answer
                empty = False if answer.options else True
            elif question.kind == QuestionConstants.KIND_POINT:
                answer_data["point"] = answer.point
                empty = False if answer.point else True
            if not empty:
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


def submit_response(
    response: ResponseData, public_query: PublicQueryData | None = None
) -> ResponseData:
    engine = SubmitResponseEngine(response=response, public_query=public_query)
    return engine.submit()


class PublicQueryResultReturner(ServiceBase):
    def __init__(self, public_query: PublicQueryData):
        self.public_query = public_query

    def get(self) -> PublicQueryResultData:
        return PublicQueryResultData(
            query=self.public_query,
            total_responses=response_providers.get_total_responses_by_query_uuid(
                query_uuid=self.public_query.uuid
            ),
            anonymous_responses=(
                response_providers.get_anonymous_responses_by_query_uuid(
                    query_uuid=self.public_query.uuid
                )
            ),
            partial_responses=self._get_partial_responses(),
            answer_results=self._get_answer_results(),
        )

    def _get_partial_responses(self) -> list[ResponseData]:
        responses_queryset = response_providers.get_responses_by_query_uuid(
            query_uuid=self.public_query.uuid
        )
        return [
            ResponseData(
                query_uuid=response.query_id,
                send_at=response.send_at,
                email=response.email,
                rut=response.rut,
            )
            for response in responses_queryset[
                : PublicQueryResultConstants.LENGTH_PARTIAL_LIST
            ]
        ]

    def _get_answer_results(self) -> list[AnswerResultData]:
        answers_result_data_list = []
        for question in self.public_query.questions:
            result = AnswerResultData(
                question=question,
                total=answer_providers.get_total_answers_by_question_uuid(
                    question_uuid=question.uuid
                ),
            )
            if question.kind in PublicQueryResultConstants.QUESTION_KIND_WITH_LIST:
                queryset = answer_providers.get_answers_by_question_uuid(
                    question_uuid=question.uuid
                )
                partial_list = self._build_answer_data_list(
                    instances=queryset[: PublicQueryResultConstants.LENGTH_PARTIAL_LIST]
                )
                result.partial_list = partial_list
            elif question.kind == QuestionConstants.KIND_SELECT:
                result.options = self._get_option_results(
                    question=question, total=result.total
                )
            answers_result_data_list.append(result)
        return answers_result_data_list

    def _get_option_results(
        self, question: QuestionData, total: int
    ) -> list[OptionResultData]:
        option_results = []
        for option in question.options:
            option_total = answer_providers.get_total_answers_by_option_uuid(
                option_uuid=option.uuid,
            )
            option_result = OptionResultData(
                option_uuid=option.uuid,
                option_name=option.name,
                total=option_total,
                percent=(option_total / total) * 100,
            )
            option_results.append(option_result)
        return option_results


def get_public_query_result(public_query: PublicQueryData) -> PublicQueryResultData:
    returner = PublicQueryResultReturner(public_query=public_query)
    return returner.get()


class AnswerResultReturner(ServiceBase):
    def __init__(self, question_uuid: UUID, page_size: int | None = None):
        try:
            question = question_providers.get_question_by_uuid(uuid=question_uuid)
        except Question.DoesNotExist:
            raise QuestionDoesNotExist
        if question.kind not in QuestionConstants.RESULT_AVAILABLE_KINDS:
            raise QuestionDoesNotExist

        self.question = question
        self.page_size = page_size or PublicQueryResultConstants.DEFAULT_PAGE_SIZE
        assert isinstance(self.page_size, int)
        self.question_data = build_dataclass_from_model_instance(
            klass=QuestionData,
            instance=question,
            uuid=question.id,
            query_uuid=question.query_id,
            index=None,
        )

    def get(self, page_num: int | None = None) -> AnswerResultData:
        queryset = answer_providers.get_answers_by_question_uuid(
            question_uuid=self.question_data.uuid
        )
        extra_kwargs = {}
        if self.question.kind == QuestionConstants.KIND_POINT:
            partial_list = queryset
            total = queryset.count()
        else:
            paginator = Paginator(object_list=queryset, per_page=self.page_size)
            total = paginator.count
            page = paginator.get_page(number=page_num)
            partial_list = page.object_list
            extra_kwargs = {"num_pages": paginator.num_pages}
        partial_list = self._build_answer_data_list(instances=partial_list)

        return AnswerResultData(
            question=self.question_data,
            total=total,
            partial_list=partial_list,
            page_num=page_num,
            **extra_kwargs,
        )


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
