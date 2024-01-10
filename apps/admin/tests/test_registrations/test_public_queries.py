from django.urls import reverse

from apps.public_queries.lib.constants import PublicQueryConstants
from apps.public_queries.models import PublicQuery
from apps.public_queries.tests import recipes as public_query_recipes


class TestPublicQueryAdmin:
    change_list_pattern = "django_admin:public_queries_publicquery_changelist"
    add_pattern = "django_admin:public_queries_publicquery_add"
    change_pattern = "django_admin:public_queries_publicquery_change"

    def test_changelist(self, admin_client):
        public_query_recipes.public_query_recipe.make()
        url = reverse(self.change_list_pattern)
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_search(self, admin_client):
        url = reverse(self.change_list_pattern)
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_add(self, admin_client):
        url = reverse(self.add_pattern)
        response = admin_client.get(url)
        assert response.status_code == 200
        fake_name = "fake-name"
        response = admin_client.post(
            url,
            data={
                "kind": PublicQueryConstants.KIND_OPEN,
                "name": fake_name,
                "max_responses": 0,
                "auth_email": PublicQueryConstants.AUTH_OPTIONAL,
                "auth_rut": PublicQueryConstants.AUTH_OPTIONAL,
                "questions-TOTAL_FORMS": 0,
                "questions-INITIAL_FORMS": 0,
                "allowedresponder_set-TOTAL_FORMS": 0,
                "allowedresponder_set-INITIAL_FORMS": 0,
                "url_code": "Xkjsd,",
            },
        )
        assert response.status_code == 302
        assert PublicQuery.objects.filter(name=fake_name).exists()

    def test_view_user(self, admin_client):
        public_query = public_query_recipes.public_query_recipe.make()
        url = reverse(self.change_pattern, kwargs={"object_id": public_query.pk})
        response = admin_client.get(url)
        assert response.status_code == 200


class TestResponseAdmin:
    change_list_pattern = "django_admin:public_queries_response_changelist"
    add_pattern = "django_admin:public_queries_response_add"
    change_pattern = "django_admin:public_queries_response_change"

    def test_changelist(self, admin_client):
        public_query_recipes.response_recipe.make()
        url = reverse(self.change_list_pattern)
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_search(self, admin_client):
        public_query_recipes.response_recipe.make()
        url = reverse(self.change_list_pattern)
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_view_user(self, admin_client):
        response = public_query_recipes.response_recipe.make()
        url = reverse(self.change_pattern, kwargs={"object_id": response.pk})
        response = admin_client.get(url)
        assert response.status_code == 200
