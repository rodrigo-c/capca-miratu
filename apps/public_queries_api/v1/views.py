from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.public_queries.lib.dataclasses import QueryMapResultData
from apps.public_queries.lib.exceptions import (
    CantSubmitPublicQueryError,
    PublicQueryDoesNotExist,
)
from apps.public_queries.services import (
    can_submit_public_query,
    get_public_query_map_result,
)
from apps.public_queries_api.v1.serializers.map_result import QueryMapResultSerializer


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


class PublicQueryAuth(ViewSet):
    @action(detail=True, methods=["post"])
    def can_submit(self, request, pk) -> Response:
        try:
            can_submit_public_query(
                query_identifier=pk,
                email=request.data.get("email"),
                rut=request.data.get("rut"),
            )
        except PublicQueryDoesNotExist:
            raise Http404
        except CantSubmitPublicQueryError as error:
            return Response(error.data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_200_OK)
