from datetime import datetime

from rest_framework import serializers

from apps.admin_api.lib.constants import PublicQueryErrorConstants
from apps.admin_api.v1.serializers.generic import (
    PublicQuerySerializer,
    QuestionOptionSerializer,
    QuestionSerializer,
)
from apps.public_queries.lib.constants import (
    CreatePublicQueryConstants,
    PublicQueryConstants,
    QuestionConstants,
)
from apps.public_queries.lib.dataclasses import (
    PublicQueryData,
    QuestionData,
    QuestionOptionData,
)


class CreateQuestionOptionSerializer(QuestionOptionSerializer):
    uuid = None
    question_uuid = None
    order = serializers.IntegerField(default=0)
    name = serializers.CharField(required=False, allow_null=True)


class CreateQuestionSerializer(QuestionSerializer):
    uuid = None
    index = None
    query_uuid = None
    kind = serializers.ChoiceField(choices=QuestionConstants.KIND_CHOICES)
    max_answers = serializers.IntegerField(default=1, min_value=1)
    text_max_length = serializers.IntegerField(default=255, min_value=1)
    order = serializers.IntegerField(default=0)
    options = serializers.ListField(
        child=CreateQuestionOptionSerializer(),
        allow_empty=True,
        required=False,
    )

    def validate(self, data) -> dict:
        if data["kind"] == QuestionConstants.KIND_SELECT_IMAGE:
            data = self._set_empty_option_names(data=data)
        options = data.get("options")
        if data["kind"] in [
            QuestionConstants.KIND_SELECT,
            QuestionConstants.KIND_SELECT_IMAGE,
        ]:
            self._validate_options_empty(options=options)
            self._validate_options_equals(options=options)
        return data

    def _validate_options_empty(self, options: list) -> dict:
        if (
            options is None
            or len(options) < 2
            or not any(opt["name"] for opt in options)
        ):
            raise serializers.ValidationError(
                {"options": PublicQueryErrorConstants.OPTIONS_EMPTY}
            )

    def _validate_options_equals(self, options: list) -> dict:
        option_names = [option["name"] for option in options]
        if len(option_names) > len(set(option_names)):
            raise serializers.ValidationError(
                {"options": PublicQueryErrorConstants.OPTIONS_EQUALS}
            )

    def _set_empty_option_names(self, data: dict) -> dict:
        options = [
            {
                **option,
                "name": (
                    option["name"]
                    if option.get("name")
                    else f"*q-opt-img-{data['order']}-{option['order']}"
                ),
            }
            for option in data.get("options", [])
        ]
        if options:
            data["options"] = options
        return data


class CreatePublicQuerySerializer(PublicQuerySerializer):
    uuid = None
    is_active = None
    url_code = None
    questions = serializers.ListField(child=CreateQuestionSerializer(), min_length=1)
    kind = serializers.ChoiceField(
        choices=PublicQueryConstants.KIND_CHOICES,
        default=PublicQueryConstants.KIND_OPEN,
    )

    def validate(self, data) -> dict:
        if (
            all(
                isinstance(data.get(field), datetime)
                for field in ["start_at", "end_at"]
            )
            and data["start_at"] >= data["end_at"]
        ):
            raise serializers.ValidationError(
                {"start_at": CreatePublicQueryConstants.INVALID_START_END_AT}
            )
        return data

    def get_dataclass(self) -> PublicQueryData:
        questions = [
            QuestionData(
                **{
                    **question,
                    "uuid": question.get("uuid"),
                    "query_uuid": question.get("query_uuid"),
                    "options": self._get_options(question),
                }
            )
            for question in self.validated_data["questions"]
        ]
        return PublicQueryData(
            **{
                **self.validated_data,
                "uuid": self.validated_data.get("uuid"),
                "questions": questions,
            }
        )

    def _get_options(self, question: dict) -> list[QuestionOptionData]:
        if question.get("options") is not None:
            return [
                QuestionOptionData(**{"uuid": None, "question_uuid": None, **option})
                for option in question["options"]
            ]


class UpdateQuestionOptionSerializer(QuestionOptionSerializer):
    uuid = serializers.UUIDField(required=False, allow_null=True)
    question_uuid = serializers.UUIDField(required=False, allow_null=True)


class UpdateQuestionSerializer(CreateQuestionSerializer):
    uuid = serializers.UUIDField(required=False, allow_null=True)
    options = serializers.ListField(
        child=UpdateQuestionOptionSerializer(),
        allow_empty=True,
        required=False,
    )


class UpdatePublicQuerySerializer(CreatePublicQuerySerializer):
    uuid = serializers.UUIDField(required=True)
    questions = serializers.ListField(child=UpdateQuestionSerializer(), min_length=1)


class UpdateQuestionSerializer(serializers.Serializer):
    question_uuid = serializers.UUIDField(required=True)
    image = serializers.ImageField(required=False, allow_null=True)


class UpdateQuestionOptionImageSerializer(serializers.Serializer):
    option_uuid = serializers.UUIDField(required=True)
    image = serializers.ImageField(required=False, allow_null=True)


class UpdateResponseVisiblity(serializers.Serializer):
    response_uuid = serializers.UUIDField(required=True)
    visible = serializers.BooleanField(required=True)
