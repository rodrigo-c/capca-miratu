import base64
import io
from uuid import UUID

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.mobile_api.v1.serializers import (
    ConsultaDetailSerializer,
    ConsultaListSerializer,
    SubmitSerializer,
)
from apps.public_queries import services as public_queries_services
from apps.public_queries.lib.constants import PublicQueryConstants
from apps.public_queries.lib.dataclasses import AnswerData, ResponseData
from apps.public_queries.lib.exceptions import (
    CantSubmitPublicQueryError,
    PublicQueryDoesNotExist,
)


class ConsultaViewSet(ViewSet):
    def list(self, request) -> Response:
        all_queries = public_queries_services.get_public_query_list()
        active_open = [
            q
            for q in all_queries
            if q.is_active and q.kind == PublicQueryConstants.KIND_OPEN
        ]
        serializer = ConsultaListSerializer(many=True, instance=active_open)
        return Response(serializer.data)

    def retrieve(self, request, pk=None) -> Response:
        try:
            consulta = public_queries_services.get_public_query(
                identifier=pk, active=True
            )
        except PublicQueryDoesNotExist:
            raise Http404
        if consulta.kind != PublicQueryConstants.KIND_OPEN:
            raise Http404
        serializer = ConsultaDetailSerializer(instance=consulta)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None) -> Response:
        try:
            consulta = public_queries_services.get_public_query(
                identifier=pk, active=True
            )
        except PublicQueryDoesNotExist:
            raise Http404
        if consulta.kind != PublicQueryConstants.KIND_OPEN:
            raise Http404

        serializer = SubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        rut = data.get("rut") or None
        email = data.get("email") or None

        try:
            public_queries_services.can_submit_public_query(
                query_identifier=pk,
                email=email,
                rut=rut,
            )
        except CantSubmitPublicQueryError as error:
            return Response(error.data, status=status.HTTP_401_UNAUTHORIZED)

        location = None
        if data.get("location"):
            loc = data["location"]
            location = Point(float(loc["lng"]), float(loc["lat"]))

        answers = [
            self._build_answer_data(answer_data)
            for answer_data in data["answers"]
        ]

        response_data = ResponseData(
            query_uuid=consulta.uuid,
            answers=answers,
            email=email,
            rut=rut,
            location=location,
        )

        try:
            submitted = public_queries_services.submit_response(
                response=response_data, public_query=consulta
            )
        except AssertionError as error:
            return Response(
                {"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"response_uuid": str(submitted.uuid)}, status=status.HTTP_201_CREATED
        )

    def _build_answer_data(self, data: dict) -> AnswerData:
        point = None
        if data.get("point"):
            p = data["point"]
            point = Point(float(p["lng"]), float(p["lat"]))

        image = None
        if data.get("image"):
            image = self._base64_to_file(data["image"])

        options = [UUID(str(opt)) for opt in data.get("options", [])]

        return AnswerData(
            question_uuid=data["question_uuid"],
            text=data.get("text") or None,
            image=image,
            options=options or None,
            point=point,
        )

    def _base64_to_file(self, b64_string: str) -> InMemoryUploadedFile:
        # Strip data URI prefix if present (e.g. "data:image/jpeg;base64,...")
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        raw = base64.b64decode(b64_string)
        file_io = io.BytesIO(raw)
        return InMemoryUploadedFile(
            file=file_io,
            field_name="image",
            name="upload.jpg",
            content_type="image/jpeg",
            size=len(raw),
            charset=None,
        )
