from django.db import transaction

from apps.public_queries.domain_logic.restrictions import query_can_edit_questions
from apps.public_queries.domain_logic.returners import PublicQueryReturner
from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.public_queries.lib.dataclasses import PublicQueryData, QuestionData
from apps.public_queries.models import PublicQuery, Question, QuestionOption
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import question as question_providers
from apps.public_queries.providers import question_option as question_option_providers


class PublicQueryFactory:
    def __init__(self, data: PublicQueryData):
        self.data = data

    def create(self, user_id=None) -> PublicQueryData:
        with transaction.atomic():
            public_query = self._create_query(user_id=user_id)
            self._create_questions()
            self._create_options()
        return PublicQueryReturner(identifier=public_query.id).get()

    def update(self) -> PublicQueryData:
        with transaction.atomic():
            public_query = self._update_query()
            if query_can_edit_questions(public_query=public_query):
                self._update_questions()
                self._update_options()
        return PublicQueryReturner(identifier=public_query.id).get()

    def _create_query(self, user_id) -> PublicQuery:
        public_query_kwargs = self._get_public_query_kwargs()
        public_query = public_query_providers.create_public_query(
            user_id=user_id, **public_query_kwargs
        )
        self.data.uuid = public_query.id
        return public_query

    def _update_query(self) -> PublicQuery:
        public_query = public_query_providers.get_public_query_by_uuid(
            uuid=self.data.uuid
        )
        public_query_kwargs = self._get_public_query_kwargs()
        fields_for_update = set()
        for field, value in public_query_kwargs.items():
            if hasattr(public_query, field) and getattr(public_query, field) != value:
                fields_for_update.add(field)
                setattr(public_query, field, value)
        public_query.save(update_fields=list(fields_for_update))
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

    def _update_questions(self) -> list[Question]:
        current_questions = question_providers.get_questions_by_public_query_uuid(
            uuid=self.data.uuid
        )
        current_questions_map = {
            str(question.id): question for question in current_questions
        }
        updated_questions_map = {}
        new_questions = []
        for question in self.data.questions:
            question_kwargs = self._get_question_kwargs(question=question)
            if question.uuid and str(question.uuid) in current_questions_map:
                question_kwargs["uuid"] = question.uuid
                updated_questions_map[str(question.uuid)] = question_kwargs
            else:
                new_questions.append(question_kwargs)
        if updated_questions_map:
            question_providers.bulk_update_questions(
                data_list=list(updated_questions_map.values())
            )
        created_questions = (
            question_providers.bulk_create_questions(data_list=new_questions)
            if new_questions
            else []
        )
        question_uuids_for_delete = [
            question_uuid
            for question_uuid in current_questions_map
            if question_uuid not in updated_questions_map
        ]
        if question_uuids_for_delete:
            question_providers.delete_question_by_uuids(uuids=question_uuids_for_delete)
        created_questions_by_order = {
            question.order: question for question in created_questions
        }
        for question in self.data.questions:
            if not question.uuid:
                question.uuid = created_questions_by_order[question.order].id

        return question_providers.get_questions_by_public_query_uuid(
            uuid=self.data.uuid
        )

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
            "default_point": question.default_point or None,
            "default_zoom": question.default_zoom or None,
        }

    def _get_options_data_list(self) -> list:
        options_data_list = []
        for question in self.data.questions:
            if question.kind in [
                QuestionConstants.KIND_SELECT,
                QuestionConstants.KIND_SELECT_IMAGE,
            ]:
                options_kwargs = [
                    {
                        "uuid": option.uuid,
                        "question_uuid": question.uuid,
                        "name": option.name,
                        "order": option.order or 0,
                    }
                    for option in question.options or []
                ]
                options_data_list.extend(options_kwargs)
        return options_data_list

    def _create_options(self) -> list[QuestionOption]:
        options_data_list = self._get_options_data_list()
        return (
            question_option_providers.bulk_create_question_options(
                data_list=options_data_list
            )
            if options_data_list
            else []
        )

    def _update_options(self) -> list[QuestionOption]:
        options_data_list = self._get_options_data_list()
        current_options = question_option_providers.get_question_options_by_query_uuid(
            query_uuid=self.data.uuid
        )
        current_options_map = {str(option.id): option for option in current_options}
        options_for_update = {}
        options_for_create = []
        for option in options_data_list:
            if option["uuid"] and str(option["uuid"]) in current_options_map:
                options_for_update[str(option["uuid"])] = option
            else:
                options_for_create.append(option)
        if options_for_update:
            changed_options = [
                option
                for option_uuid, option in options_for_update.items()
                if any(
                    option[field] != getattr(current_options_map[option_uuid], field)
                    for field in ["name", "order"]
                )
            ]
            if changed_options:
                question_option_providers.bulk_update_question_options(
                    data_list=changed_options
                )
        question_option_providers.bulk_create_question_options(
            data_list=options_for_create
        ) if options_for_create else []
        options_uuids_for_delete = [
            option_uuid
            for option_uuid in current_options_map
            if option_uuid not in options_for_update
        ]
        if options_uuids_for_delete:
            question_option_providers.delete_question_option_by_uuids(
                uuids=options_uuids_for_delete
            )
        return question_option_providers.get_question_options_by_query_uuid(
            query_uuid=self.data.uuid
        )
