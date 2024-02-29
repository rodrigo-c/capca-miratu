from datetime import datetime

from rest_framework import serializers

from apps.admin_api.lib.constants import PublicQueryErrorConstants
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
from apps.public_queries_api.v1.serializers.generic import (
    AnswerSerializer,
    PublicQuerySerializer,
    QuestionOptionSerializer,
    QuestionSerializer,
    ResponseSerializer,
)


class OptionResultSerializer(serializers.Serializer):
    option_uuid = serializers.UUIDField()
    option_name = serializers.CharField()
    total = serializers.IntegerField()
    percent = serializers.FloatField()


class AnswerResultSerializer(serializers.Serializer):
    question = QuestionSerializer()
    total = serializers.IntegerField()
    partial_list = serializers.ListField(child=AnswerSerializer())
    options = serializers.ListField(child=OptionResultSerializer())


class PublicQueryResultSerializer(serializers.Serializer):
    query = PublicQuerySerializer()
    total_responses = serializers.IntegerField()
    anonymous_responses = serializers.IntegerField()
    partial_responses = serializers.ListField(child=ResponseSerializer())
    answer_results = serializers.ListField(child=AnswerResultSerializer())
    links = serializers.DictField(child=serializers.CharField(), allow_empty=True)


class CreateQuestionOptionSerializer(QuestionOptionSerializer):
    uuid = None
    question_uuid = None
    order = serializers.IntegerField(default=0)


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
        options = data.get("options")
        if data["kind"] == QuestionConstants.KIND_SELECT:
            self._validate_options_empty(options=options)
            self._validate_options_equals(options=options)
        return data

    def _validate_options_empty(self, options: list) -> dict:
        if options is None or len(options) < 2:
            raise serializers.ValidationError(
                {"options": PublicQueryErrorConstants.OPTIONS_EMPTY}
            )

    def _validate_options_equals(self, options: list) -> dict:
        option_names = [option["name"] for option in options]
        if len(option_names) > len(set(option_names)):
            raise serializers.ValidationError(
                {"options": PublicQueryErrorConstants.OPTIONS_EQUALS}
            )


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
                CreatePublicQueryConstants.INVALID_START_END_AT
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
            for question in self.data["questions"]
        ]
        return PublicQueryData(
            **{**self.data, "uuid": self.data.get("uuid"), "questions": questions}
        )

    def _get_options(self, question: dict) -> list[QuestionOptionData]:
        if question.get("options") is not None:
            return [
                QuestionOptionData(uuid=None, question_uuid=None, **option)
                for option in question["options"]
            ]


class UpdateQuestionSerializer(CreateQuestionSerializer):
    uuid = serializers.UUIDField(required=False, allow_null=True)


class UpdatePublicQuerySerializer(CreatePublicQuerySerializer):
    uuid = serializers.UUIDField(required=True)
    questions = serializers.ListField(child=UpdateQuestionSerializer(), min_length=1)
