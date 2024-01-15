from uuid import UUID

from rest_framework import serializers

from apps.public_queries_api.v1.serializers.generic import (
    AnswerSerializer,
    PublicQuerySerializer,
    QuestionSerializer,
    ResponseSerializer,
)


class OptionResultSerializer(serializers.Serializer):
    option_uuid: UUID
    option_name: str
    total: int
    percent: float


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
