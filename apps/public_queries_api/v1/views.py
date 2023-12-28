from django.http import Http404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.public_queries.lib.dataclasses import QueryMapResultData
from apps.public_queries.lib.exceptions import PublicQueryDoesNotExist
from apps.public_queries.services import get_public_query_map_result
from apps.public_queries_api.v1.serializers import QueryMapResultSerializer


class PublicQueryMapResult(ViewSet):
    def retrieve(self, request, pk) -> Response:
        public_query_result = self._get_public_query_map_result(identifier=pk)
        serializer = QueryMapResultSerializer(instance=public_query_result)
        return Response(serializer.data)

    def _get_public_query_map_result(self, identifier: str) -> QueryMapResultData:
        try:
            public_query_result = get_public_query_map_result(identifier=identifier)
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query_result
