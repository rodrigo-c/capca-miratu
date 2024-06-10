from io import BytesIO
from uuid import UUID

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import AnswerData, ResponseData
from apps.public_queries.models import PublicQuery
from apps.public_queries.services import get_public_query, submit_response
from apps.utils.random import get_random_url_code


def create_fake_uploaded_image(field_name="images", size=(50, 50), color=(256, 0, 0)):
    image = Image.new("RGBA", size=size, color=color)
    image_file = BytesIO()
    image.save(image_file, "PNG")
    image_file.seek(0)
    return InMemoryUploadedFile(
        image_file,
        name="fake-image.png",
        field_name=field_name,
        content_type="image/png",
        size=len(image_file.getvalue()),
        charset=None,
    )


def create_test_data(public_query_uuid: UUID, response_num: int = 100) -> None:
    public_query = PublicQuery.objects.get(id=public_query_uuid)
    public_query_data = get_public_query(identifier=public_query.id)
    returned_responses = []
    alternate = True
    for index in range(response_num):
        alternate = not alternate
        index_name = f"{index}-{get_random_url_code()}"
        base_color_index = index if index < 100 else index // 100
        answers_list = []
        for question in public_query.questions.all():
            answer_data = AnswerData(
                question_uuid=question.id,
            )
            add = question.required or alternate
            if question.kind == QuestionConstants.KIND_TEXT and add:
                answer_data.text = f"Esto es un comentario {index_name}"
                answers_list.append(answer_data)
            elif question.kind == QuestionConstants.KIND_IMAGE and add:
                answer_data.image = create_fake_uploaded_image(
                    color=(
                        base_color_index,
                        50 + base_color_index,
                        100 + base_color_index,
                    )
                )
                answers_list.append(answer_data)
            elif (
                question.kind
                in [QuestionConstants.KIND_SELECT, QuestionConstants.KIND_SELECT_IMAGE]
                and add
            ):
                option = (
                    question.options.first() if alternate else question.options.last()
                )
                answer_data.options = [option.id]
                answers_list.append(answer_data)
            elif question.kind == QuestionConstants.KIND_POINT and add:
                answer_data.point = Point(
                    [float(f"-73.{index}"), float(f"-36.{index}")],
                    srid=4326,
                )
                answers_list.append(answer_data)
            alternate = not alternate
        response_data = ResponseData(
            query_uuid=public_query.id,
            answers=answers_list,
            email=f"persona.{index_name}@{index_name}.cl" if alternate else None,
            rut=f"1{str(index).zfill(7)}-0" if alternate else None,
            location=Point(
                [float(f"-73.{index}"), float(f"-36.{index}")],
                srid=4326,
            )
            if alternate
            else None,
        )
        returned_response = submit_response(
            response=response_data, public_query=public_query_data
        )
        returned_responses.append(returned_response)
    return returned_responses
