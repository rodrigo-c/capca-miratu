from collections import defaultdict
from datetime import datetime
from uuid import UUID

from django.utils import timezone

from apps.public_queries.domain_logic.base import ServiceBase
from apps.public_queries.domain_logic.returners import PublicQueryReturner
from apps.public_queries.lib.constants import QueryMapResultConstants, QuestionConstants
from apps.public_queries.lib.dataclasses import (
    AnswerData,
    PointResultData,
    QueryMapResultData,
    ResponseData,
)
from apps.public_queries.models import Answer, Response
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.providers import response as response_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


class QueryMapResultReturner(ServiceBase):
    def __init__(self, identifier: UUID | str):
        self.public_query = PublicQueryReturner(identifier=identifier).get()
        self.public_query.questions = self.public_query.questions or []

    def get(self) -> QueryMapResultData:
        point_list = self._get_point_list()
        response_range = (
            self._get_response_range(point_list=point_list) if point_list else None
        )
        return QueryMapResultData(
            query=self.public_query,
            point_list=point_list,
            fetch_at=timezone.now(),
            response_range=response_range,
        )

    def _get_point_list(self) -> list[PointResultData]:
        point_question_map = {
            question.uuid: question
            for question in self.public_query.questions
            if question.kind == QuestionConstants.KIND_POINT
        }
        responses_queryset = response_providers.get_responses_by_query_uuid(
            query_uuid=self.public_query.uuid, visible=True
        )
        answers_queryset = answer_providers.get_answers_by_query_uuid(
            query_uuid=self.public_query.uuid
        ).prefetch_related("options")
        answers_by_response_uuid = defaultdict(list)
        for answer in answers_queryset:
            answers_by_response_uuid[answer.response_id].append(answer)

        point_list = []
        for response in responses_queryset:
            answers = answers_by_response_uuid[response.id]
            partial_point_list = self._get_point_data_list_from_response(
                response=response,
                answers=answers,
                point_question_map=point_question_map,
            )
            point_list.extend(partial_point_list)
        return point_list

    def _get_point_data_list_from_response(
        self,
        response: Response,
        answers: list[Answer],
        point_question_map: dict,
    ) -> list[PointResultData]:
        filtered_answers = [
            answer for answer in answers if answer.question_id not in point_question_map
        ]
        response_data = self._to_response_dataclass(
            instance=response, answers=filtered_answers
        )
        if not point_question_map:
            point_data = PointResultData(
                response=response_data,
                location=response.location,
                related_label=QueryMapResultConstants.LOCATION,
                question_index=None,
            )
            return [point_data]
        answers_by_question_uuid = {answer.question_id: answer for answer in answers}
        point_data_list = []
        for point_question_uuid in point_question_map:
            question = point_question_map[point_question_uuid]
            answer = answers_by_question_uuid.get(point_question_uuid)
            if answer:
                point_data = PointResultData(
                    response=response_data,
                    location=answer.point,
                    related_label=question.name,
                    question_index=question.index,
                )
                point_data_list.append(point_data)
        return point_data_list

    def _to_response_dataclass(
        self, instance: Response, answers: list[Answer] | None = None
    ) -> ResponseData:
        answers_data_list = [
            self._to_answer_dataclass(instance=answer) for answer in answers
        ]
        return ResponseData(
            uuid=instance.id,
            query_uuid=instance.query_id,
            send_at=instance.send_at,
            email=instance.email,
            rut=instance.rut,
            answers=answers_data_list,
        )

    def _to_answer_dataclass(self, instance: Answer) -> AnswerData:
        return build_dataclass_from_model_instance(
            klass=AnswerData,
            instance=instance,
            uuid=instance.id,
            response_uuid=instance.response_id,
            question_uuid=instance.question_id,
            image=instance.image.url if instance.image else None,
            options=list(instance.options.values()),
            send_at=None,
        )

    def _get_response_range(self, point_list: list[PointResultData]) -> tuple[datetime]:
        point_list.sort(key=lambda point: point.response.send_at)
        return (point_list[0].response.send_at, point_list[-1].response.send_at)
