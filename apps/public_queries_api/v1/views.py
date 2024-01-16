import re

from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import QueryMapResultData
from apps.public_queries.lib.exceptions import (
    CantSubmitPublicQueryError,
    PublicQueryDoesNotExist,
)
from apps.public_queries.services import (
    can_submit_public_query,
    get_public_query_map_result,
    get_public_query_responses_data,
)
from apps.public_queries_api.v1.lib.constants import PublicQueryDataResultConstants
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


class PublicQueryDataResult(ViewSet):
    def retrieve(self, request, pk) -> Response:
        public_query_result = self._get_public_query_data_result(identifier=pk)
        verbose_fields = self._get_verbose_fields(dataset=public_query_result)
        public_query_result["verbose_fields"] = verbose_fields
        public_query_result["simpletables_config"] = self._get_simpletables_config(
            public_query=public_query_result["query"], fields=verbose_fields
        )
        return Response(public_query_result)

    def _get_public_query_data_result(self, identifier: str) -> dict:
        try:
            public_query_result = get_public_query_responses_data(identifier=identifier)
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query_result

    def _get_verbose_fields(self, dataset: dict) -> list[str]:
        verbose_fields = {}
        for field in dataset["fields"]:
            verbose = PublicQueryDataResultConstants.VERBOSE_FIELDS.get(field, field)
            if "pregunta_" in field:
                verbose = field.replace("_", " ").capitalize()
            verbose_fields[field] = verbose
        return verbose_fields

    def _get_simpletables_config(self, public_query, fields) -> dict:
        columns = []
        for index, (field, label) in enumerate(fields.items()):
            column = {"select": index, "type": "html", "cellClass": "cell"}
            if field == "send_at":
                column["type"] = "date"
                column["format"] = "MYSQL"
            if "pregunta_" in field:
                index = int(re.search(r"\d+", field)[0]) - 1
                question = public_query["questions"][index]
                if question["kind"] == QuestionConstants.KIND_TEXT:
                    column["cellClass"] = "cell-tooltip value-text"
                if question["kind"] == QuestionConstants.KIND_IMAGE:
                    column["cellClass"] = "cell-tooltip value-image"
                if question["kind"] == QuestionConstants.KIND_POINT:
                    column["cellClass"] = "cell-tooltip value-point"
                if question["kind"] == QuestionConstants.KIND_SELECT:
                    column["cellClass"] = "cell-tooltip value-select"
            else:
                column["cellClass"] = f"cell {field}"
            columns.append(column)
        return {
            "locale": "es-cl",
            "perPageSelect": [5, 10, 50, 100],
            "columns": columns,
            "data": {
                "headings": fields.values(),
                "data": [],
            },
        }


class PublicQueryAuth(ViewSet):
    @action(detail=True, methods=["post"])
    def can_submit(self, request, pk) -> Response:
        try:
            can_submit_public_query(
                query_identifier=pk,
                email=request.data.get("email"),
                rut=request.data.get("rut"),
                secret_key=request.data.get("sk"),
            )
        except PublicQueryDoesNotExist:
            raise Http404
        except CantSubmitPublicQueryError as error:
            return Response(error.data, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_200_OK)
