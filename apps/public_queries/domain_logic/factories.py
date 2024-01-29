from collections import defaultdict

from django.db import transaction

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.public_queries.lib.dataclasses import (
    PublicQueryData,
    QuestionData,
    QuestionOptionData,
)
from apps.public_queries.models import PublicQuery, Question, QuestionOption
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import question as question_providers
from apps.public_queries.providers import question_option as question_option_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


class PublicQueryFactory:
    def __init__(self, data: PublicQueryData):
        self.data = data

    def create(self, user_id=None) -> PublicQueryData:
        with transaction.atomic():
            public_query = self._create_query(user_id=user_id)
            questions = self._create_questions()
            options = self._create_options()
        public_query_data = self._to_dataclass(
            public_query=public_query,
            questions=questions,
            options=options,
        )
        return public_query_data

    def _create_query(self, user_id) -> PublicQuery:
        public_query_kwargs = self._get_public_query_kwargs()
        public_query = public_query_providers.create_public_query(
            user_id=user_id, **public_query_kwargs
        )
        self.data.uuid = public_query.id
        return public_query

    def _get_public_query_kwargs(self) -> dict:
        public_query_kwargs = {
            "name": self.data.name,
            "kind": self.data.kind,
            "description": self.data.description,
            "start_at": self.data.start_at,
            "end_at": self.data.end_at,
            "active": self.data.active or False,
            "max_responses": (
                self.data.max_responses or PublicQueryConstants.NOT_MAX_RESPONSES
            ),
            "auth_rut": self.data.auth_rut or PublicQueryConstants.AUTH_OPTIONAL,
            "auth_email": self.data.auth_email or PublicQueryConstants.AUTH_OPTIONAL,
        }
        return public_query_kwargs

    def _create_questions(self) -> list[Question]:
        question_data_list = []
        for question in self.data.questions:
            question_kwargs = self._get_question_kwargs(question=question)
            question_data_list.append(question_kwargs)
        created_questions = question_providers.bulk_create_questions(
            data_list=question_data_list
        )
        assert len(created_questions) == len(self.data.questions)
        for index, question in enumerate(created_questions):
            self.data.questions[index].uuid = question.id
        return created_questions

    def _get_question_kwargs(self, question: QuestionData) -> dict:
        return {
            "query_uuid": self.data.uuid,
            "kind": question.kind,
            "name": question.name,
            "description": question.description,
            "order": question.order or 0,
            "required": question.required or False,
            "text_max_length": question.text_max_length or 255,
            "max_answers": question.max_answers or 1,
            # "min_answers": question.min_answers or 1,
        }

    def _create_options(self) -> list[QuestionOption]:
        options_data_list = []
        for index, question in enumerate(self.data.questions):
            if question.kind == QuestionConstants.KIND_SELECT:
                options_kwargs = [
                    {
                        "question_uuid": question.uuid,
                        "name": option.name,
                        "order": option.order or 0,
                    }
                    for option in question.options or []
                ]
                options_data_list.extend(options_kwargs)
        return (
            question_option_providers.bulk_create_question_options(
                data_list=options_data_list
            )
            if options_data_list
            else []
        )

    def _to_dataclass(
        self,
        public_query: PublicQuery,
        questions: list[Question],
        options: list[QuestionOption],
    ) -> PublicQueryData:
        options_by_question_uuid = defaultdict(list)
        for option in options:
            option_data = build_dataclass_from_model_instance(
                klass=QuestionOptionData,
                instance=option,
                uuid=option.id,
                question_uuid=option.question_id,
            )
            options_by_question_uuid[option.question_id].append(option_data)
        question_data_list = []
        for index, question in enumerate(questions):
            question_data = build_dataclass_from_model_instance(
                klass=QuestionData,
                instance=question,
                uuid=question.id,
                query_uuid=question.query_id,
                options=options_by_question_uuid.get(question.id),
                index=index,
            )
            question_data_list.append(question_data)
        return build_dataclass_from_model_instance(
            klass=PublicQueryData,
            instance=public_query,
            uuid=public_query.id,
            questions=question_data_list,
        )
