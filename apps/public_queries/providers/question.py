from uuid import UUID

from django.db.models import QuerySet

from apps.public_queries.models import Question


def get_questions_by_public_query_uuid(uuid: UUID) -> "QuerySet[Question]":
    return Question.objects.filter(query_id=uuid)


def get_question_by_uuid(uuid: UUID) -> Question:
    return Question.objects.get(id=uuid)


def bulk_create_questions(data_list: list[dict]) -> list[Question]:
    fields = [
        "kind",
        "name",
        "description",
        "order",
        "required",
        "text_max_length",
        "max_answers",
        "min_answers",
    ]
    instances = []
    for data in data_list:
        instance_kwargs = {field: data[field] for field in fields if field in data}
        instance_kwargs["query_id"] = data["query_uuid"]
        instance = Question(**instance_kwargs)
        instances.append(instance)
    return Question.objects.bulk_create(objs=instances)
