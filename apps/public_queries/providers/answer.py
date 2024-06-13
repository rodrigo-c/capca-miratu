from io import BytesIO
from uuid import UUID

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

from apps.public_queries.models import Answer


def _set_image_thumbs(answers: list[Answer]) -> list[Answer]:
    def _get_image_file(original, resolution):
        image = Image.open(original)
        image.thumbnail(resolution)
        image_file = BytesIO()
        image.save(image_file, "PNG")
        return image_file

    def _get_inmemoryuploadedfile(img_file, original_field) -> InMemoryUploadedFile:
        return InMemoryUploadedFile(
            img_file,
            name=None,
            field_name=None,
            content_type="image/png",
            size=img_file.tell(),
            charset=None,
        )

    for answer in answers:
        thumb_file = _get_image_file(answer.image.file, (200, 200))
        thumb_medium_file = _get_image_file(answer.image.file, (500, 500))
        answer.thumb.save(
            answer.image.name,
            _get_inmemoryuploadedfile(img_file=thumb_file, original_field=answer.image),
            save=False,
        )
        answer.thumb_medium.save(
            answer.image.name,
            _get_inmemoryuploadedfile(
                img_file=thumb_medium_file, original_field=answer.image
            ),
            save=False,
        )
    return answers


def bulk_create_answers(answers: list[dict]) -> list[Answer]:
    instances = [Answer(**answer) for answer in answers]
    objs = Answer.objects.bulk_create(objs=instances)
    objs_with_imgs = [obj for obj in objs if obj.image.name is not None]
    if objs_with_imgs:
        objs_with_thumbs = _set_image_thumbs(answers=objs_with_imgs)
        Answer.objects.bulk_update(
            objs=objs_with_thumbs, fields=["thumb", "thumb_medium"]
        )
    return objs


def get_total_answers_by_question_uuid(question_uuid: UUID) -> int:
    return Answer.objects.filter(question_id=question_uuid).count()


def get_answers_by_question_uuid(question_uuid: UUID) -> list[Answer]:
    return Answer.objects.filter(question_id=question_uuid)


def get_answers_by_query_uuid(query_uuid: UUID) -> list[Answer]:
    return Answer.objects.filter(question__query_id=query_uuid)


def get_total_answers_by_option_uuid(option_uuid: UUID) -> int:
    return Answer.objects.filter(options=option_uuid).count()
