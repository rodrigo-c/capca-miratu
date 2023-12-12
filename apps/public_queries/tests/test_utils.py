import pytest

from apps.public_queries.utils import create_test_data


@pytest.mark.django_db
def test_create_test_data(ended_public_query):
    returned_responses = create_test_data(
        public_query_uuid=ended_public_query.id, response_num=10
    )
    assert len(returned_responses) == 10
