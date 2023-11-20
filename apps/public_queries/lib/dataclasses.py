from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


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
