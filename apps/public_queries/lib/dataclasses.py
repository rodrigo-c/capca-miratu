from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


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
    index: int
    required: bool
    max_answers: int
    text_max_length: int | None = None
    description: str | None = None
    options: list | None = None


@dataclass
class PublicQueryData:
    uuid: UUID
    kind: str
    name: str
    active: bool
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    image: str | None = None
    questions: list[QuestionData] | None = None


@dataclass
class AnswerData:
    question_uuid: UUID
    text: str | None = None
    image: str | None = None
    options: list | None = None
    uuid: UUID | None = None
    response_uuid: UUID | None = None


@dataclass
class ResponseData:
    query_uuid: UUID
    answers: list[AnswerData]
    uuid: UUID | None = None
    send_at: datetime | None = None
    email: str | None = None
    rut: str | None = None
    query_data: PublicQueryData | None = None
