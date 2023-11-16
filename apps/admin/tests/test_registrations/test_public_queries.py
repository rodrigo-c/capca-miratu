from django.urls import reverse

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants
from apps.public_queries.models import PublicQuery, Question
from apps.public_queries.tests import recipes as public_query_recipes


class TestPublicQueryAdmin:
    change_list_pattern = "admin:public_queries_publicquery_changelist"
    add_pattern = "admin:public_queries_publicquery_add"
    change_pattern = "admin:public_queries_publicquery_change"

    def test_changelist(self, admin_client):
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
            data={"kind": PublicQueryConstants.KIND_OPEN, "name": fake_name},
        )
        assert response.status_code == 302
        assert PublicQuery.objects.filter(name=fake_name).exists()

    def test_view_user(self, admin_client):
        public_query = public_query_recipes.public_query_recipe.make()
        url = reverse(self.change_pattern, kwargs={"object_id": public_query.pk})
        response = admin_client.get(url)
        assert response.status_code == 200


class TestQuestionAdmin:
    change_list_pattern = "admin:public_queries_question_changelist"
    add_pattern = "admin:public_queries_question_add"
    change_pattern = "admin:public_queries_question_change"

    def test_changelist(self, admin_client):
        url = reverse(self.change_list_pattern)
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_search(self, admin_client):
        url = reverse(self.change_list_pattern)
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_add(self, admin_client):
        public_query = public_query_recipes.public_query_recipe.make()
        url = reverse(self.add_pattern)
        response = admin_client.get(url)
        assert response.status_code == 200
        fake_name = "fake-name"
        response = admin_client.post(
            url,
            data={
                "kind": QuestionConstants.KIND_TEXT,
                "name": fake_name,
                "query": public_query.id,
                "order": 0,
                "max_answers": 1,
                "text_max_length": 255,
            },
        )
        assert response.status_code == 302
        assert Question.objects.filter(name=fake_name).exists()

    def test_view_user(self, admin_client):
        question = public_query_recipes.question_recipe.make()
        url = reverse(self.change_pattern, kwargs={"object_id": question.pk})
        response = admin_client.get(url)
        assert response.status_code == 200
