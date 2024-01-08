import pytest

from apps.public_queries.providers import (
    allowed_responder as allowed_responder_provider,
)


@pytest.mark.django_db
class TestAllowedResponderExists:
    def test_exists(self, make_closed_public_query):
        valid_email = "valid@ema.il"
        public_query = make_closed_public_query(emails=[valid_email])
        secret_key = public_query.allowedresponder_set.first().email_code

        assert (
            allowed_responder_provider.allowed_responder_exists(
                query_uuid=public_query.id, email=valid_email, email_code=secret_key
            )
            is True
        )

    def test_not_exists(self, make_closed_public_query):
        valid_email = "invalid@ema.il"
        public_query = make_closed_public_query(emails=[valid_email])
        secret_key = public_query.allowedresponder_set.first().email_code[:-2]
        assert (
            allowed_responder_provider.allowed_responder_exists(
                query_uuid=public_query.id, email=valid_email, email_code=secret_key
            )
            is False
        )
