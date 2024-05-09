import re
from io import BytesIO
from uuid import UUID

from django.http import FileResponse, Http404
from django.urls import reverse
from rest_framework import status as response_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ViewSet

from geojson import Feature, FeatureCollection, Point
from openpyxl import Workbook

from apps.admin_api.lib.constants import PublicQueryDataResultConstants
from apps.admin_api.v1.serializers.edit import (
    CreatePublicQuerySerializer,
    UpdatePublicQuerySerializer,
    UpdateQuestionSerializer,
    UpdateResponseVisiblity,
)
from apps.admin_api.v1.serializers.generic import PublicQuerySerializer
from apps.admin_api.v1.serializers.results import (
    PublicQueryResultSerializer,
    QueryMapResultSerializer,
)
from apps.public_queries import services as public_queries_services
from apps.public_queries.lib.constants import QuestionConstants
from apps.public_queries.lib.dataclasses import PublicQueryData, QueryMapResultData
from apps.public_queries.lib.exceptions import (
    PublicQueryCreateError,
    PublicQueryDoesNotExist,
    PublicQueryUpdateError,
    QuestionDoesNotExist,
)


class PublicQueryManager(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        data_list = self.filter_by_user(
            public_queries=public_queries_services.get_public_query_list()
        )
        serializer = PublicQuerySerializer(many=True, instance=data_list)
        show_user_email = request.user.is_superuser if request.user else False
        return Response({"list": serializer.data, "show_user_email": show_user_email})

    def retrieve(self, request, pk=None) -> Response:
        public_query = self.get_public_query(identifier=pk)
        result = public_queries_services.get_public_query_result(
            public_query=public_query
        )
        kwargs = {"uuid": public_query.url_code}
        result.links = {
            "submit": reverse("public_queries:submit", kwargs=kwargs),
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

    def delete(self, request, pk=None) -> Response:
        public_query = self.get_public_query(identifier=pk)
        if request.data.get("confirmation") == "TRUE":
            if public_queries_services.delete_public_query(uuid=public_query.uuid):
                return Response({}, status=response_status.HTTP_202_ACCEPTED)
        return Response({}, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=["post"])
    def update_question_image(self, request) -> Response:
        serializer = UpdateQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            image_url = public_queries_services.update_question_image(
                **serializer.validated_data
            )
        except QuestionDoesNotExist:
            raise Http404
        success_data = {
            "question_uuid": serializer.validated_data["question_uuid"],
            "image_url": image_url,
        }
        return Response(success_data, status=response_status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"])
    def update_response_visibility(self, request) -> Response:
        serializer = UpdateResponseVisiblity(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            visible = public_queries_services.update_response_visibility(
                **serializer.validated_data
            )
        except QuestionDoesNotExist:
            raise Http404
        success_data = {
            "response_uuid": serializer.validated_data["response_uuid"],
            "visible": visible,
        }
        return Response(success_data, status=response_status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["get"])
    def map(self, request, pk) -> Response:
        public_query_result = self.get_public_query_map_result(identifier=pk)
        serializer = QueryMapResultSerializer(instance=public_query_result)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def data(self, request, pk) -> Response:
        public_query_result = self._get_public_query_data_result(identifier=pk)
        verbose_fields = self._get_verbose_fields(dataset=public_query_result)
        public_query_result["verbose_fields"] = verbose_fields
        public_query_result["simpletables_config"] = self._get_simpletables_config(
            public_query=public_query_result["query"], fields=verbose_fields
        )
        return Response(public_query_result)

    @action(detail=True, methods=["get"])
    def share(self, request, pk=None) -> FileResponse:
        public_query = self.get_public_query(identifier=pk)
        pdf_file = public_queries_services.get_public_query_share_document(
            public_query=public_query, host=request.get_host()
        )
        filename = f"consulta-{public_query.url_code}.pdf"
        content_type = (
            "application/force-download"
            if self.request.GET.get("k") == "download"
            else "application/pdf"
        )
        return FileResponse(pdf_file, filename=filename, content_type=content_type)

    @action(detail=True, methods=["get"])
    def excel(self, request, pk=None) -> FileResponse:
        public_query_result = self._get_public_query_data_result(identifier=pk)
        verbose_fields = self._get_verbose_fields(dataset=public_query_result)
        excel_file = self._get_excel_file(
            dataset=public_query_result, verbose_fields=verbose_fields
        )
        filename = f"consulta-{public_query_result['query']['url_code']}-data.xlsx"
        return FileResponse(
            excel_file,
            filename=filename,
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )

    @action(detail=True, methods=["get"])
    def geojson(self, request, pk) -> Response:
        public_query_result = self.get_public_query_map_result(identifier=pk)
        geojson = self._get_gsojson_file(public_query_result=public_query_result)
        filename = f"consulta-{public_query_result.query.url_code}-geo.json"
        response = FileResponse(
            geojson, filename=filename, content_type="application/force-download"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

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

    def get_public_query_map_result(self, identifier: str) -> QueryMapResultData:
        try:
            public_query_result = public_queries_services.get_public_query_map_result(
                identifier=identifier
            )
            if not self.filter_by_user(public_queries=[public_query_result.query]):
                raise PublicQueryDoesNotExist
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query_result

    def _get_public_query_data_result(self, identifier: str) -> dict:
        try:
            public_query_result = (
                public_queries_services.get_public_query_responses_data(
                    identifier=identifier
                )
            )
            created_by_email = public_query_result["query"]["created_by_email"]
            if (
                not self.request.user.is_superuser
                and self.request.user.email != created_by_email
            ):
                raise PublicQueryDoesNotExist
        except PublicQueryDoesNotExist:
            raise Http404
        return public_query_result

    def _get_verbose_fields(self, dataset: dict) -> list:
        verbose_fields = {}
        for field in dataset["fields"]:
            verbose = PublicQueryDataResultConstants.VERBOSE_FIELDS.get(field, field)
            if "pregunta_" in field:
                verbose = field.replace("_", " ").capitalize()
            verbose_fields[field] = verbose
        return verbose_fields

    def _get_simpletables_config(self, public_query, fields) -> dict:
        columns = []
        headings = []
        for index, (field, label) in enumerate(fields.items()):
            heading = {"label": label}
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
                heading["desc"] = question["name"]
            else:
                column["cellClass"] = f"cell {field}"
            headings.append(heading)
            columns.append(column)
        return {
            "locale": "es-cl",
            "perPageSelect": [5, 10, 50, 100],
            "columns": columns,
            "data": {
                "headings": headings,
                "data": [],
            },
            "fixedColumns": True,
            "labels": {
                "placeholder": "Buscar...",
                "info": "Mostrando {start} a {end} de {rows} respuestas",
                "perPage": "Consultas por página",
            },
        }

    def _get_excel_file(self, dataset, verbose_fields) -> BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.append(list(verbose_fields.values()))
        for data in dataset.get("dataset", []):
            row = [
                str(value) if value else ""
                for field, value in data.items()
                if field != "uuid"
            ]
            ws.append(row)
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        return excel_file

    def _get_gsojson_file(self, public_query_result: QueryMapResultData) -> BytesIO:
        query = public_query_result.query
        query_properties = {
            "name": query.name,
            "description": query.description,
            "start_at": str(query.start_at),
            "end_at": str(query.end_at),
            "questions": {
                question.index: {
                    "name": question.name,
                    "description": question.description,
                }
                for question in query.questions
                if question.kind == QuestionConstants.KIND_POINT
            },
        }
        features = []
        for point_data in public_query_result.point_list:
            if point_data.question_index:
                point = Point(point_data.location)
                response = point_data.response
                feature_properties = {
                    "question_index": point_data.question_index,
                    "response": {
                        "send_at": str(response.send_at) if response.send_at else None,
                        "rut": str(response.rut) if response.rut else None,
                        "email": str(response.email) if response.email else None,
                    },
                }
                feature = Feature(
                    id=f"{response.uuid}::{point_data.question_index}",
                    geometry=point,
                    properties=feature_properties,
                )
                features.append(feature)
        feature_collection = FeatureCollection(
            features,
            id=query.url_code,
            properties=query_properties,
        )
        return str(feature_collection)
