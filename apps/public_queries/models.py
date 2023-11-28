import uuid

from django.contrib.gis.db import models

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.utils.random import get_random_url_code


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublicQuery(BaseModel):
    kind = models.CharField(
        choices=PublicQueryConstants.KIND_CHOICES,
        blank=False,
        null=False,
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    start_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    end_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    active = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True, upload_to="public_queries/images/")
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="public_queries",
    )
    url_code = models.CharField(
        max_length=15,
        unique=True,
        default=get_random_url_code,
    )

    class Meta:
        ordering = ["start_at"]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.name} ({self.id})"


class Question(BaseModel):
    query = models.ForeignKey(
        PublicQuery,
        on_delete=models.CASCADE,
        null=False,
        related_name="questions",
    )
    kind = models.CharField(
        choices=QuestionConstants.KIND_CHOICES,
        blank=False,
        null=False,
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    order = models.IntegerField(default=0)
    required = models.BooleanField(default=True)
    text_max_length = models.IntegerField(default=255)
    max_answers = models.IntegerField(null=False, blank=False, default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.name} ({self.id})"


class Response(BaseModel):
    query = models.ForeignKey(
        PublicQuery,
        on_delete=models.CASCADE,
        null=False,
        related_name="responses",
    )
    send_at = models.DateTimeField(null=False)
    location = models.PointField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    rut = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ["send_at"]


class Answer(BaseModel):
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        null=False,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=False,
        related_name="answers",
    )
    text = models.TextField(
        blank=True,
        null=True,
    )
    image = models.ImageField(
        null=True, blank=True, upload_to="public_queries/answers/images/"
    )

    class Meta:
        ordering = ["question__order"]
