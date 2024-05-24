from uuid import UUID

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet

from apps.public_queries.models import Question

QUESTION_FIELDS = [
    "kind",
    "name",
    "description",
    "order",
    "required",
    "text_max_length",
    "max_answers",
    "min_answers",
    "default_point",
    "default_zoom",
]


def get_questions_by_public_query_uuid(uuid: UUID) -> "QuerySet[Question]":
    return Question.objects.filter(query_id=uuid)


def get_question_by_uuid(uuid: UUID) -> Question:
    return Question.objects.get(id=uuid)


def bulk_create_questions(data_list: list[dict]) -> list[Question]:
    instances = []
    for data in data_list:
        instance_kwargs = {
            field: data[field] for field in QUESTION_FIELDS if field in data
        }
        instance_kwargs["query_id"] = data["query_uuid"]
        instance = Question(**instance_kwargs)
        instances.append(instance)
    return Question.objects.bulk_create(objs=instances)


def bulk_update_questions(data_list: list[dict]) -> list[Question]:
    instances = []
    fields_for_update = set()
    for data in data_list:
        instance_kwargs = {
            field: data[field] for field in QUESTION_FIELDS if field in data
        }
        fields_for_update = fields_for_update | set(list(instance_kwargs))
        instance_kwargs["id"] = data["uuid"]
        instance_kwargs["query_id"] = data["query_uuid"]
        instance = Question(**instance_kwargs)
        instances.append(instance)
    return Question.objects.bulk_update(objs=instances, fields=list(fields_for_update))


def update_question_image(
    question_uuid: UUID, image: InMemoryUploadedFile
) -> str | None:
    instance = Question.objects.get(id=question_uuid)
    instance.image = image
    instance.save(update_fields=["image"])
    return instance.image.url if instance.image else None


def delete_question_by_uuids(uuids: list[UUID]) -> None:
    Question.objects.filter(id__in=uuids).delete()
