from uuid import UUID

from django.conf import settings

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import (
    PublicQueryData,
    QuestionData,
    QuestionOptionData,
)
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.models import PublicQuery, Question
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import question as question_providers
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
