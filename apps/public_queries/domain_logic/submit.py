from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.public_queries.domain_logic.base import ServiceBase
from apps.public_queries.domain_logic.returners import PublicQueryReturner
from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PublicQueryData,
    ResponseData,
)
from apps.public_queries.models import Answer, Response
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.providers import response as response_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance
from apps.utils.rut import format_rut


class SubmitResponseEngine(ServiceBase):
    def __init__(
        self, response: ResponseData, public_query: PublicQueryData | None = None
    ):
        if not public_query:
            public_query = PublicQueryReturner(identifier=response.query_uuid).get()

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
            rut=format_rut(self.response.rut) if self.response.rut else None,
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
