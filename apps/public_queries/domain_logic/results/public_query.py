from django.core.paginator import Paginator

from apps.public_queries.domain_logic.base import ServiceBase
from apps.public_queries.lib.constants import (
    PublicQueryResultConstants,
    QuestionConstants,
)
from apps.public_queries.lib.dataclasses import (
    AnswerResultData,
    OptionResultData,
    PublicQueryData,
    PublicQueryResultData,
    QuestionData,
    ResponseData,
)
from apps.public_queries.models import Response
from apps.public_queries.providers import answer as answer_providers
from apps.public_queries.providers import response as response_providers


class PublicQueryResultReturner(ServiceBase):
    def __init__(self, public_query: PublicQueryData, page_size: int | None = None):
        self.page_size = page_size or PublicQueryResultConstants.DEFAULT_PAGE_SIZE
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

    def get_responses(self, page_num: int | None = None) -> PublicQueryResultData:
        page_num = page_num if isinstance(page_num, int) and page_num > 0 else 1
        partial_responses = self._get_paginated_responses(page_num=page_num)
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
            partial_responses=partial_responses,
            answer_results=None,
            page_num=page_num,
            num_pages=self.response_paginator.num_pages,
        )

    def _get_partial_responses(self) -> list[ResponseData]:
        responses_queryset = response_providers.get_responses_by_query_uuid(
            query_uuid=self.public_query.uuid
        )
        return self._to_response_dataclasses(
            instances=responses_queryset[
                : PublicQueryResultConstants.LENGTH_PARTIAL_LIST
            ]
        )

    def _to_response_dataclasses(self, instances: list[Response]) -> list[ResponseData]:
        return [
            ResponseData(
                query_uuid=response.query_id,
                send_at=response.send_at,
                email=response.email,
                rut=response.rut,
            )
            for response in instances
        ]

    def _get_paginated_responses(self, page_num: int) -> list[ResponseData]:
        responses_queryset = response_providers.get_responses_by_query_uuid(
            query_uuid=self.public_query.uuid
        )
        paginator = Paginator(object_list=responses_queryset, per_page=self.page_size)
        page = paginator.get_page(number=page_num)
        self.response_paginator = paginator
        return self._to_response_dataclasses(instances=page.object_list)

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
                percent=(option_total / total) * 100 if total else 0.0,
            )
            option_results.append(option_result)
        return option_results
