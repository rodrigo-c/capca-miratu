from rest_framework import serializers

from drf_extra_fields.geo_fields import PointField

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants


class QuestionOptionSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    question_uuid = serializers.UUIDField()
    name = serializers.CharField()
    order = serializers.IntegerField()


class QuestionSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    query_uuid = serializers.UUIDField()
    kind = serializers.ChoiceField(choices=QuestionConstants.KIND_CHOICES)
    name = serializers.CharField()
    order = serializers.IntegerField()
    required = serializers.BooleanField()
    max_answers = serializers.IntegerField()
    text_max_length = serializers.IntegerField()
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    options = serializers.ListField(child=QuestionOptionSerializer())
    index = serializers.IntegerField()


class PublicQuerySerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    kind = serializers.ChoiceField(choices=PublicQueryConstants.KIND_CHOICES)
    name = serializers.CharField()
    active = serializers.BooleanField()
    is_active = serializers.BooleanField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    start_at = serializers.DateTimeField(required=False, allow_null=True)
    end_at = serializers.DateTimeField(required=False, allow_null=True)
    image = serializers.CharField(required=False)
    questions = serializers.ListField(child=QuestionSerializer())
    url_code = serializers.CharField()


class AnswerSerializer(serializers.Serializer):
    question_uuid = serializers.UUIDField()
    text = serializers.CharField()
    image = serializers.CharField()
    options = serializers.ListField(child=serializers.JSONField())
    point = PointField()
    response_uuid = serializers.UUIDField()
    send_at = serializers.DateTimeField()


class ResponseSerializer(serializers.Serializer):
    query_uuid = serializers.UUIDField()
    answers = serializers.ListField(child=AnswerSerializer())
    uuid = serializers.UUIDField()
    send_at = serializers.DateTimeField()
    email = serializers.DateTimeField()
    rut = serializers.DateTimeField()
    location = PointField()
