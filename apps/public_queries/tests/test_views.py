from datetime import datetime

import pytest
from django.urls import reverse
from django.utils.timezone import make_aware

from freezegun import freeze_time

from apps.public_queries.tests.recipes import public_query_recipe


@pytest.mark.django_db
class TestPublicQuerySubmit:
    public_query_pattern = "public_queries:submit"

    def test_get_success(self, client):
        public_query = public_query_recipe.make(active=True)
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        response = client.get(url)
        assert response.status_code == 200

    def test_get_not_active(self, client):
        public_query = public_query_recipe.make()
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        response = client.get(url)
        assert response.status_code == 404

    def test_out_of_start_time(self, client):
        public_query = public_query_recipe.make(
            active=True, start_at=make_aware(datetime(2023, 1, 2))
        )
        url = reverse(self.public_query_pattern, kwargs={"uuid": public_query.id})
        with freeze_time("2023-01-01"):
            response = client.get(url)
        assert response.status_code == 404
