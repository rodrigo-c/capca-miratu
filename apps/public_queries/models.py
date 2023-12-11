import uuid

from django.contrib.gis.db import models
from django.utils import timezone

from apps.public_queries.lib.constants import (
    AnswerConstants,
    PublicQueryConstants,
    QuestionConstants,
    QuestionOptionConstants,
    ResponseConstants,
)
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
        verbose_name = PublicQueryConstants.VERBOSE_NAME
        verbose_name_plural = PublicQueryConstants.VERBOSE_NAME_PLURAL

    def __str__(self) -> str:
        return f"{self.name} ({self.url_code})"

    @property
    def is_active(self) -> bool:
        if not self.active:
            return False
        now = timezone.now()
        is_after_start = self.start_at is None or self.start_at < now
        is_before_end = self.end_at is None or self.end_at > now
        if is_after_start and is_before_end:
            return True
        return False


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
        verbose_name = QuestionConstants.VERBOSE_NAME
        verbose_name_plural = QuestionConstants.VERBOSE_NAME_PLURAL

    def __str__(self) -> str:
        return (
            f"[{self.order}][{self.kind}] {self.name[:100]}"
            f"{('...' if len(self.name) > 100 else '')}"
        )


class QuestionOption(BaseModel):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=False,
        related_name="options",
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = QuestionOptionConstants.VERBOSE_NAME
        verbose_name_plural = QuestionOptionConstants.VERBOSE_NAME_PLURAL

    def __str__(self) -> str:
        return f"{self.name} [{self.id}]"


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
        verbose_name = ResponseConstants.VERBOSE_NAME
        verbose_name_plural = ResponseConstants.VERBOSE_NAME_PLURAL

    def __str__(self) -> str:
        return (
            f"[{str(self.send_at)[:19]}] > {self.query.name[:50]}"
            f"{('...' if len(self.query.name) > 50 else '')}"
        )


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
    options = models.ManyToManyField(
        QuestionOption,
        related_name="answers",
        limit_choices_to=models.Q(question_id=models.F("question_id")),
    )
    point = models.PointField(null=True, blank=True)

    class Meta:
        ordering = ["question__order"]
        verbose_name = AnswerConstants.VERBOSE_NAME
        verbose_name_plural = AnswerConstants.VERBOSE_NAME_PLURAL

    def __str__(self) -> str:
        return f"> {self.question}"
