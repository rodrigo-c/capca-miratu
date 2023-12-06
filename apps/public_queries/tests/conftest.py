from io import BytesIO

import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

from apps.public_queries.lib.dataclasses import QuestionData
from apps.public_queries.tests import recipes
from apps.utils.dataclasses import build_dataclass_from_model_instance


@pytest.fixture
def public_query():
    return recipes.public_query_recipe.make()


@pytest.fixture
def question():
    return recipes.question_recipe.make()


@pytest.fixture
def question_option():
    return recipes.question_option_recipe.make()


@pytest.fixture
def question_data():
    question = recipes.question_recipe.make(required=True)
    return build_dataclass_from_model_instance(
        klass=QuestionData,
        instance=question,
        uuid=question.id,
        index=0,
        query_uuid=question.query_id,
    )


@pytest.fixture
def response():
    return recipes.response_recipe.make()


@pytest.fixture
def answer():
    return recipes.answer_recipe.make()


@pytest.fixture
def uploaded_image(field_name="images"):
    image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
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
