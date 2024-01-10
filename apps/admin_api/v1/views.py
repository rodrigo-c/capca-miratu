from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.public_queries.services import get_public_query_list
from apps.public_queries_api.v1.serializers.generic import PublicQuerySerializer


class PublicQueryManager(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        data_list = get_public_query_list()
        serializer = PublicQuerySerializer(many=True, instance=data_list)
        return Response({"list": serializer.data})
