from uuid import UUID

from django.core.paginator import Paginator

from apps.public_queries.domain_logic.base import ServiceBase
from apps.public_queries.lib.constants import (
    PublicQueryResultConstants,
    QuestionConstants,
)
from apps.public_queries.lib.dataclasses import AnswerResultData, QuestionData
from apps.public_queries.lib.exceptions import QuestionDoesNotExist
from apps.public_queries.models import Question
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.providers import question as question_providers
from apps.utils.dataclasses import build_dataclass_from_model_instance


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
            options=None,
        )

    def get(self, page_num: int | None = None) -> AnswerResultData:
        queryset = answer_providers.get_answers_by_question_uuid(
            question_uuid=self.question_data.uuid
        )
        extra_kwargs = {
            "query_name": self.question.query.name,
            "query_urlcode": self.question.query.url_code,
            "page_num": page_num,
            "options": None,
        }
        if self.question.kind == QuestionConstants.KIND_POINT:
            partial_list = queryset
            total = queryset.count()
        else:
            paginator = Paginator(object_list=queryset, per_page=self.page_size)
            total = paginator.count
            page = paginator.get_page(number=page_num)
            partial_list = page.object_list
            extra_kwargs.update({"num_pages": paginator.num_pages})
        partial_list = self._build_answer_data_list(
            instances=partial_list,
            with_response=True,
        )

        return AnswerResultData(
            question=self.question_data,
            total=total,
            partial_list=partial_list,
            **extra_kwargs,
        )
