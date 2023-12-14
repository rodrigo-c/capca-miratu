from uuid import UUID

from django.db.models import QuerySet

from apps.public_queries.models import Question


def get_questions_by_public_query_uuid(uuid: UUID) -> "QuerySet[Question]":
    return Question.objects.filter(query_id=uuid)


def get_question_by_uuid(uuid: UUID) -> Question:
    return Question.objects.get(id=uuid)
