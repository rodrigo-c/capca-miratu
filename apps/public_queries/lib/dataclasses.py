from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class QuestionData:
    uuid: UUID
    query_uuid: UUID
    name: str
    order: int
    index: int
    required: bool
    max_answers: int
    text_max_length: int | None = None
    description: str | None = None


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
