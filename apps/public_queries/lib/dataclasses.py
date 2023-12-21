import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.contrib.gis.geos import Point


@dataclass
class QuestionOptionData:
    uuid: UUID
    question_uuid: UUID
    name: str
    order: int


@dataclass
class QuestionData:
    uuid: UUID
    query_uuid: UUID
    kind: str
    name: str
    order: int
    required: bool
    max_answers: int
    text_max_length: int | None = None
    description: str | None = None
    options: list | None = None
    index: int | None = None


@dataclass
class PublicQueryData:
    uuid: UUID
    kind: str
    name: str
    active: bool
    is_active: bool
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    image: str | None = None
    questions: list[QuestionData] | None = None
    url_code: str | None = None


@dataclass
class AnswerData:
    question_uuid: UUID
    text: str | None = None
    image: str | None = None
    options: list | None = None
    point: Point = None
    uuid: UUID | None = None
    response_uuid: UUID | None = None
    send_at: datetime | None = None


@dataclass
class ResponseData:
    query_uuid: UUID
    answers: list[AnswerData] | None = None
    uuid: UUID | None = None
    send_at: datetime | None = None
    email: str | None = None
    rut: str | None = None
    location: Point | None = None
    query_data: PublicQueryData | None = None


@dataclass
class OptionResultData:
    option_uuid: UUID
    option_name: str
    total: int
    percent: float


@dataclass
class AnswerResultData:
    question: QuestionData
    total: int
    partial_list: list | None = None
    options: list[OptionResultData] | None = None
    page_num: int | None = None
    num_pages: int | None = None
    query_name: str | None = None
    query_urlcode: str | None = None

    @property
    def partial_list_json(self) -> str:
        def _set_value(value) -> dict:
            if value is None:
                return
            if isinstance(value, Point):
                return list(reversed(list(value)))
            return str(value)

        serialized_partial_list = [
            {field: _set_value(value=value) for field, value in answer.__dict__.items()}
            for answer in self.partial_list
        ]
        return json.dumps(serialized_partial_list)


@dataclass
class PublicQueryResultData:
    query: PublicQueryData
    total_responses: int
    anonymous_responses: int
    partial_responses: list[ResponseData]
    answer_results: list[AnswerResultData]
    page_num: int | None = None
    num_pages: int | None = None

    @property
    def has_pagination(self) -> bool:
        return self.page_num and self.num_pages


@dataclass
class PointResultData:
    response: ResponseData
    location: Point
    related_label: str


@dataclass
class QueryMapResultData:
    query: PublicQueryData
    point_list: list[PointResultData]
    fetch_at: datetime
