import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_public_query_map_result(api_client, ended_public_query):
    url = reverse(
        "public_queries_api:v1:query-map-result-detail",
        kwargs={"pk": ended_public_query.url_code},
    )
    response = api_client.get(url)
    assert response.status_code == 200
