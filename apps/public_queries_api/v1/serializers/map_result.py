from rest_framework import serializers

from drf_extra_fields.geo_fields import PointField

from apps.public_queries_api.v1.serializers.generic import (
    PublicQuerySerializer,
    ResponseSerializer,
)


class PointResultSerializer(serializers.Serializer):
    response = ResponseSerializer()
    location = PointField()
    related_label = serializers.CharField()


class QueryMapResultSerializer(serializers.Serializer):
    query = PublicQuerySerializer()
    point_list = PointResultSerializer(many=True)
    fetch_at = serializers.DateTimeField()
