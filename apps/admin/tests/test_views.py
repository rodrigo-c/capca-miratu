import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestUserLoginView:
    url = reverse("admin:login")

    def test_success(self, client, user):
        password = "new-password"
        user.set_password(password)
        user.save()
        response = client.post(
            self.url, data={"username": user.email, "password": password}
        )
        assert response.status_code == 302

    def test_fail(self, client):
        response = client.post(
            self.url, data={"username": "u@ser.email", "password": "1"}
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminEntryPoint:
    url = reverse("admin:entry-point")

    def test_get(self, client, user):
        client.force_login(user)
        response = client.get(self.url)
        assert response.status_code == 200
