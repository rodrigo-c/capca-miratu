from rest_framework import serializers

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants


class QuestionOptionMobileSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    order = serializers.IntegerField()
    image = serializers.CharField(required=False, allow_null=True)


class QuestionMobileSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    kind = serializers.ChoiceField(choices=QuestionConstants.KIND_CHOICES)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    order = serializers.IntegerField()
    index = serializers.IntegerField()
    required = serializers.BooleanField()
    max_answers = serializers.IntegerField()
    min_answers = serializers.IntegerField(default=1)
    text_max_length = serializers.IntegerField()
    options = serializers.ListField(child=QuestionOptionMobileSerializer())
    image = serializers.CharField(required=False, allow_null=True)
    default_point = serializers.SerializerMethodField()
    default_zoom = serializers.IntegerField(required=False, allow_null=True)

    def get_default_point(self, obj):
        if obj.default_point is None:
            return None
        # GEOSGeometry Point stores as (x=lon, y=lat)
        return {"lng": obj.default_point[0], "lat": obj.default_point[1]}


class ConsultaListSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    url_code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    start_at = serializers.DateTimeField(required=False, allow_null=True)
    end_at = serializers.DateTimeField(required=False, allow_null=True)
    auth_rut = serializers.ChoiceField(choices=PublicQueryConstants.AUTH_CHOICES)
    auth_email = serializers.ChoiceField(choices=PublicQueryConstants.AUTH_CHOICES)
    max_responses = serializers.IntegerField(required=False, allow_null=True)
    image = serializers.CharField(required=False, allow_null=True)
    total_responses = serializers.IntegerField(required=False, allow_null=True)


class ConsultaDetailSerializer(ConsultaListSerializer):
    questions = serializers.ListField(child=QuestionMobileSerializer())


class SubmitAnswerSerializer(serializers.Serializer):
    question_uuid = serializers.UUIDField()
    text = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    options = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    point = serializers.DictField(required=False, allow_null=True)
    image = serializers.CharField(required=False, allow_null=True)  # base64


class SubmitSerializer(serializers.Serializer):
    rut = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    location = serializers.DictField(required=False, allow_null=True)  # {lat, lng}
    answers = serializers.ListField(child=SubmitAnswerSerializer())
