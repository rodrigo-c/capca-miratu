from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from apps.public_queries.domain_logic.base import ServiceBase
from apps.public_queries.domain_logic.returners import PublicQueryReturner
from apps.public_queries.lib.constants import AuthConstants, PublicQueryConstants
from apps.public_queries.lib.exceptions import CantSubmitPublicQueryError
from apps.public_queries.providers import public_query as public_query_providers
from apps.public_queries.providers import response as response_providers
from apps.utils.rut import format_rut, is_valid_rut


class CanSubmitPublicQuery(ServiceBase):
    def __init__(
        self,
        query_identifier: UUID | str,
        responder_rut: str | None = None,
        responder_email: str | None = None,
    ):
        self.public_query = PublicQueryReturner(
            identifier=query_identifier, active=True
        ).get()
        self.responder = {"rut": responder_rut, "email": responder_email}
        self._is_valid = None

    def validate(self) -> None:
        self._validate_is_required()
        if self.responder["email"] and (
            self.public_query.auth_email != PublicQueryConstants.AUTH_DISABLE
            or self.public_query.kind == PublicQueryConstants.KIND_CLOSED
        ):
            self._validate_email()
        if (
            self.responder["rut"]
            and self.public_query.auth_rut != PublicQueryConstants.AUTH_DISABLE
        ):
            self._validate_rut()

    def _validate_is_required(self) -> None:
        errors = {}
        if (
            self.public_query.auth_rut == PublicQueryConstants.AUTH_REQUIRED
            and not self.responder["rut"]
        ):
            errors["rut"] = AuthConstants.RUT_REQUIRED
        if not self.responder["email"] and (
            self.public_query.auth_email == PublicQueryConstants.AUTH_REQUIRED
            or self.public_query.kind == PublicQueryConstants.KIND_CLOSED
        ):
            errors["email"] = AuthConstants.EMAIL_REQUIRED
        if errors:
            self._raise_validation(errors=errors)

    def _validate_email(self) -> None:
        error = None
        try:
            validate_email(self.responder["email"])
        except ValidationError:
            error = AuthConstants.EMAIL_INVALID

        if not error and self.public_query.kind == PublicQueryConstants.KIND_CLOSED:
            if not public_query_providers.email_is_allowed_to_public_query(
                public_query_uuid=self.public_query.uuid,
                email=self.responder["email"],
            ):
                error = AuthConstants.EMAIL_NOT_ALLOWED
        if (
            not error
            and self.public_query.max_responses > PublicQueryConstants.NOT_MAX_RESPONSES
            and self.public_query.auth_email == PublicQueryConstants.AUTH_REQUIRED
        ):
            current_responses = response_providers.count_responses_by_query_and_email(
                query_uuid=self.public_query.uuid,
                email=self.responder["email"],
            )
            if current_responses >= self.public_query.max_responses:
                error = AuthConstants.EMAIL_MAX_RESPONSES
        if error:
            self._raise_validation(errors={"email": error})

    def _validate_rut(self) -> None:
        error = None
        if not is_valid_rut(self.responder["rut"]):
            error = AuthConstants.RUT_INVALID
        elif (
            self.public_query.auth_rut == PublicQueryConstants.AUTH_REQUIRED
            and self.public_query.max_responses > PublicQueryConstants.NOT_MAX_RESPONSES
        ):
            cleaned_rut = format_rut(self.responder["rut"])
            current_responses = response_providers.count_responses_by_query_and_rut(
                query_uuid=self.public_query.uuid,
                rut=cleaned_rut,
            )
            if current_responses == self.public_query.max_responses:
                error = AuthConstants.RUT_MAX_RESPONSES
        if error:
            self._raise_validation(errors={"rut": error})

    def _raise_validation(self, errors) -> None:
        raise CantSubmitPublicQueryError(data=errors)
