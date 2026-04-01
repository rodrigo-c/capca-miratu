from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.public_queries.lib.exceptions import (
    CantSubmitPublicQueryError,
    PublicQueryDoesNotExist,
)
from apps.public_queries.services import can_submit_public_query


class PublicQueryAuth(ViewSet):
    authentication_classes = []
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
