from rest_framework import serializers

from drf_extra_fields.geo_fields import PointField

from apps.admin_api.v1.serializers.generic import (
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
    links = serializers.DictField(child=serializers.CharField(), allow_empty=True)


class PointResultSerializer(serializers.Serializer):
    response = ResponseSerializer()
    location = PointField()
    related_label = serializers.CharField()
    question_index = serializers.IntegerField(allow_null=True)


class QueryMapResultSerializer(serializers.Serializer):
    query = PublicQuerySerializer()
    point_list = PointResultSerializer(many=True)
    fetch_at = serializers.DateTimeField()
    response_range = serializers.ListField(
        child=serializers.DateTimeField(), required=False
    )
