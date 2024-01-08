import pytest

from apps.public_queries.domain_logic.auth import CanSubmitPublicQuery
from apps.public_queries.lib.constants import AuthConstants


@pytest.mark.django_db
class TestCanSubmitPublicQuery:
    def test_is_valid(self, make_closed_public_query):
        valid_email = "valid@ema.il"
        public_query = make_closed_public_query(emails=[valid_email])
        secret_key = public_query.allowedresponder_set.first().email_code

        assert (
            CanSubmitPublicQuery(
                query_identifier=public_query.id,
                responder_email=valid_email,
                secret_key=secret_key,
            ).is_valid()
            is True
        )

    def test_is_not_valid(self, make_closed_public_query):
        invalid_email = "invalid@ema.il"
        public_query = make_closed_public_query(emails=[invalid_email])
        secret_key = public_query.allowedresponder_set.first().email_code[:-2]
        fetcher = CanSubmitPublicQuery(
            query_identifier=public_query.id,
            responder_email=invalid_email,
            secret_key=secret_key,
        )
        assert fetcher.is_valid() is False
        assert fetcher.is_valid() is False
        assert fetcher._errors["email"] == AuthConstants.FORBIDDEN
