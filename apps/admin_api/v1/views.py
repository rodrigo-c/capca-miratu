from uuid import UUID

from django.http import Http404
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ViewSet

from apps.admin_api.v1.serializers import (
    CreatePublicQuerySerializer,
    PublicQueryResultSerializer,
)
from apps.public_queries import services as public_queries_services
from apps.public_queries.lib.dataclasses import PublicQueryData
from apps.public_queries.lib.exceptions import (
    PublicQueryCreateError,
    PublicQueryDoesNotExist,
)
from apps.public_queries_api.v1.serializers.generic import PublicQuerySerializer


class PublicQueryManager(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        data_list = public_queries_services.get_public_query_list()
        serializer = PublicQuerySerializer(many=True, instance=data_list)
        return Response({"list": serializer.data})

    def retrieve(self, request, pk=None) -> Response:
        public_query = self.get_public_query(identifier=pk)
        result = public_queries_services.get_public_query_result(
            public_query=public_query
        )
        kwargs = {"uuid": public_query.url_code}
        result.links = {
            "submit": reverse("public_queries:submit", kwargs=kwargs),
            "map": reverse("public_queries:query-map-result", kwargs=kwargs),
            "data": reverse("public_queries:query-data", kwargs=kwargs),
        }
        serializer = PublicQueryResultSerializer(instance=result)
        return Response(serializer.data)

    def create(self, request) -> Response:
        serializer = CreatePublicQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        public_query_data = serializer.get_dataclass()
        try:
            returned_data = public_queries_services.create_public_query(
                query_data=public_query_data
            )
        except PublicQueryCreateError:
            raise ValidationError("Unknown error")
        serializer = PublicQuerySerializer(instance=returned_data)
        return Response(serializer.data)

    def get_public_query(self, identifier: str | UUID) -> PublicQueryData:
        try:
            public_query = public_queries_services.get_public_query(
                identifier=identifier
            )
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query
