from collections import defaultdict
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from apps.public_queries.domain_logic.restrictions import query_can_edit_questions
from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.public_queries.lib.dataclasses import (
    PublicQueryData,
    QuestionData,
    QuestionOptionData,
)
from apps.public_queries.lib.exceptions import (
    PublicQueryDoesNotExist,
    PublicQueryEarring,
)
from apps.public_queries.models import Answer, PublicQuery, Question, Response
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import question as question_providers
from apps.public_queries.providers import response as response_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


class PublicQueryReturner:
    def __init__(self, identifier: UUID | str, active: bool | None = None):
        self.identifier = identifier
        if identifier == "__all__":
            self.public_queries = public_query_providers.get_public_query_list()
        else:
            self._set_obj(identifier=identifier, active=active)

    def _set_obj(self, identifier: UUID | str, active: bool) -> None:
        kwargs = {} if active is None else {"active": active}

        if len(str(identifier)) <= getattr(settings, "MAXIMUM_URL_CHARS", 5):
            public_query = self._get_obj_by_url_code(url_code=identifier, **kwargs)
        else:
            public_query = self._get_obj_by_uuid(uuid=identifier, **kwargs)
        if active and public_query.is_earring:
            raise PublicQueryEarring(public_query=public_query)
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

    def get(self) -> PublicQueryData | list[PublicQueryData]:
        if self.identifier == "__all__":
            return [
                self._to_dataclass(instance=instance, with_questions=False)
                for instance in self.public_queries
            ]
        else:
            return self._to_dataclass(instance=self.public_query)

    def _to_dataclass(self, instance, with_questions: bool = True) -> PublicQueryData:
        questions = None
        if with_questions:
            question_queryset = question_providers.get_questions_by_public_query_uuid(
                uuid=instance.id
            )
            questions = [
                build_dataclass_from_model_instance(
                    klass=QuestionData,
                    instance=question,
                    uuid=question.id,
                    query_uuid=instance.id,
                    index=index,
                    image=question.image.url if question.image else None,
                    options=self._get_options_data(question=question),
                )
                for index, question in enumerate(question_queryset)
            ]
        status_verbose = self._get_status_verbose(instance=instance)
        total_responses = response_providers.get_total_responses_by_query_uuid(
            query_uuid=instance.id
        )
        return build_dataclass_from_model_instance(
            klass=PublicQueryData,
            instance=instance,
            uuid=instance.id,
            image=instance.image.url if instance.image else None,
            questions=questions or None,
            status_verbose=status_verbose,
            created_by_email=instance.created_by.email if instance.created_by else None,
            total_responses=total_responses,
            can_edit_questions=query_can_edit_questions(public_query=instance),
        )

    def _get_status_verbose(self, instance: PublicQuery) -> str:
        now = timezone.now()
        if instance.is_active:
            code = PublicQueryConstants.STATUS_VERBOSE_ACTIVE
        elif instance.active and instance.end_at and now > instance.end_at:
            code = PublicQueryConstants.STATUS_VERBOSE_FINISHED
        elif instance.active and instance.start_at and now < instance.start_at:
            code = PublicQueryConstants.STATUS_VERBOSE_EARRING
        else:
            code = PublicQueryConstants.STATUS_VERBOSE_DRAFT
        return {"code": code, "label": PublicQueryConstants.STATUS_VERBOSE_LABELS[code]}

    def get_responses_data(self) -> list[dict]:
        responses_map = self.public_query.responses.in_bulk()
        answers_queryset = answer_providers.get_answers_by_query_uuid(
            query_uuid=self.public_query.id,
        )
        answers_map = defaultdict(list)
        for answer in answers_queryset:
            answers_map[answer.response_id].append(answer)
        responses_data = []
        questions = self.public_query.questions.all()
        questions_by_field = {
            f"pregunta_{index + 1}": question
            for index, question in enumerate(questions)
        }
        instance_fields = ["send_at", "email", "rut", "location", "visible"]
        for response_id, response in responses_map.items():
            response_data = self._get_response_data(
                response=response, fields=instance_fields
            )
            response_data["uuid"] = response_id
            answers = answers_map[response_id]
            response_data.update(
                {
                    field: self._get_answer_data_value(
                        question=question, answers=answers
                    )
                    for field, question in questions_by_field.items()
                }
            )
            responses_data.append(response_data)
        query = self._get_query_data()
        fields = instance_fields[:-1] + sorted(list(questions_by_field)) + ["visible"]
        return {
            "query": query,
            "fields": list(fields),
            "dataset": responses_data,
        }

    def _get_query_data(self) -> dict:
        query = self.get().__dict__
        query["uuid"] = str(query["uuid"])
        query["questions"] = [
            {
                **question.__dict__,
                "uuid": str(question.uuid),
                "options": (
                    [opt.name for opt in question.options] if question.options else None
                ),
            }
            for question in query["questions"] or []
        ]
        return query

    def _get_response_data(self, response: Response, fields: list[str]) -> dict:
        response_data = {}
        for field in fields:
            if field == "location":
                response_data[field] = (
                    {
                        "longitude": response.location[0],
                        "latitude": response.location[1],
                    }
                    if response.location
                    else None
                )
            else:
                value = getattr(response, field)
                response_data[field] = str(value) if value is not None else None
        return response_data

    def _get_answer_data_value(self, question: Question, answers: list[Answer]) -> str:
        answers_by_question = {
            answer.question_id: answer
            for answer in answers
            if answer.question_id == question.id
        }
        answer = answers_by_question.get(question.id)
        if answer is None:
            return ""
        if question.kind == QuestionConstants.KIND_TEXT:
            return answer.text
        if question.kind == QuestionConstants.KIND_IMAGE:
            return answer.image.url if answer.image else ""
        if question.kind in [
            QuestionConstants.KIND_SELECT,
            QuestionConstants.KIND_SELECT_IMAGE,
        ]:
            return list([option.name for option in answer.options.all()])
        if question.kind == QuestionConstants.KIND_POINT:
            return {"longitude": answer.point[0], "latitude": answer.point[1]}

    def _get_options_data(self, question: Question) -> list[QuestionOptionData]:
        if question.kind in [
            QuestionConstants.KIND_SELECT,
            QuestionConstants.KIND_SELECT_IMAGE,
        ]:
            return [
                build_dataclass_from_model_instance(
                    klass=QuestionOptionData,
                    instance=option,
                    uuid=option.id,
                    question_uuid=option.question_id,
                    image=option.image.url if option.image else None,
                )
                # TODO: use one query select for all questions instead
                for option in question.options.all()
            ]
