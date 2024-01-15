from uuid import UUID

from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.admin_api.v1.serializers import PublicQueryResultSerializer
from apps.public_queries import services as public_queries_services
from apps.public_queries.lib.dataclasses import PublicQueryData
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
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
        serializer = PublicQueryResultSerializer(instance=result)
        return Response(serializer.data)

    def get_public_query(self, identifier: str | UUID) -> PublicQueryData:
        try:
            public_query = public_queries_services.get_public_query(
                identifier=identifier
            )
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query
