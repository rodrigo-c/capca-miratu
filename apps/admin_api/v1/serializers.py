from rest_framework import serializers

from apps.public_queries_api.v1.serializers.generic import (
    AnswerSerializer,
    PublicQuerySerializer,
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
