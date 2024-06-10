from uuid import UUID

from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.public_queries.models import QuestionOption

QUESTION_OPTION_FIELDS = ["name", "order"]


def get_question_options_by_query_uuid(query_uuid: UUID) -> list[QuestionOption]:
    return QuestionOption.objects.filter(question__query_id=query_uuid)


def bulk_create_question_options(data_list: list[dict]) -> list[QuestionOption]:
    instances = []
    for data in data_list:
        instance_kwargs = {
            field: data[field] for field in QUESTION_OPTION_FIELDS if field in data
        }
        instance_kwargs["question_id"] = data["question_uuid"]
        instance = QuestionOption(**instance_kwargs)
        instances.append(instance)
    return QuestionOption.objects.bulk_create(objs=instances)


def bulk_update_question_options(data_list: list[dict]) -> list[QuestionOption]:
    instances = []
    for data in data_list:
        instance_kwargs = {
            field: data[field] for field in QUESTION_OPTION_FIELDS if field in data
        }
        instance_kwargs["id"] = data["uuid"]
        instance_kwargs["question_id"] = data["question_uuid"]
        instance = QuestionOption(**instance_kwargs)
        instances.append(instance)
    return QuestionOption.objects.bulk_update(
        objs=instances, fields=QUESTION_OPTION_FIELDS
    )


def delete_question_option_by_uuids(uuids: list[UUID]) -> None:
    return QuestionOption.objects.filter(id__in=uuids).delete()


def update_question_option_image(
    option_uuid: UUID, image: InMemoryUploadedFile
) -> str | None:
    instance = QuestionOption.objects.get(id=option_uuid)
    instance.image = image
    instance.save(update_fields=["image"])
    return instance.image.url if instance.image else None
