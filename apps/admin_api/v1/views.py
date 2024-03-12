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
    UpdatePublicQuerySerializer,
)
from apps.public_queries import services as public_queries_services
from apps.public_queries.lib.dataclasses import PublicQueryData
from apps.public_queries.lib.exceptions import (
    PublicQueryCreateError,
    PublicQueryDoesNotExist,
    PublicQueryUpdateError,
)
from apps.public_queries_api.v1.serializers.generic import PublicQuerySerializer


class PublicQueryManager(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        data_list = self.filter_by_user(
            public_queries=public_queries_services.get_public_query_list()
        )
        serializer = PublicQuerySerializer(many=True, instance=data_list)
        show_user_email = request.user.is_superuser if request.user else False
        return Response({"list": serializer.data, "show_user_email": show_user_email})

    def filter_by_user(
        self,
        public_queries: list,
    ) -> list:
        filtered_queries = filter(
            lambda query: (
                query.created_by_email == self.request.user.email
                or self.request.user.is_superuser
            ),
            public_queries,
        )
        return list(filtered_queries)

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
                query_data=public_query_data, user_id=request.user.id
            )
        except PublicQueryCreateError:
            raise ValidationError("Unknown error")
        serializer = PublicQuerySerializer(instance=returned_data)
        return Response(serializer.data)

    def update(self, request, pk=None) -> Response:
        public_query = self.get_public_query(identifier=pk)
        serializer = UpdatePublicQuerySerializer(
            data={**request.data, "uuid": public_query.uuid}
        )
        serializer.is_valid(raise_exception=True)
        public_query_data = serializer.get_dataclass()
        try:
            returned_data = public_queries_services.update_public_query(
                query_data=public_query_data
            )
        except PublicQueryUpdateError:
            raise ValidationError("Unknown error")
        serializer = PublicQuerySerializer(instance=returned_data)
        return Response(serializer.data)

    def get_public_query(self, identifier: str | UUID) -> PublicQueryData:
        try:
            public_query = public_queries_services.get_public_query(
                identifier=identifier
            )
            if not self.filter_by_user(public_queries=[public_query]):
                raise PublicQueryDoesNotExist
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query
