import re

import pytest
from django.core import mail
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


@pytest.mark.django_db
class TestUserPasswordChangeView:
    def test_change_password(self, user, client):
        old_password = "123"
        user.set_password(old_password)
        user.save()
        data = {
            "new_password1": "1SdvXsdRwe.",
            "new_password2": "1SdvXsdRwe.",
            "old_password": old_password,
        }
        client.force_login(user)
        response = client.post("/admin/password_change/", data)
        assert response.status_code == 302
        assert response.url == "/admin/login/"


@pytest.mark.django_db
class TestPasswordResetView:
    def test_update(self, user, client):
        data = {"email": user.email}
        response = client.post("/admin/password_reset/", data)
        assert response.status_code == 302
        assert len(mail.outbox) == 1


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    def test_update(self, user, client):
        data = {"email": user.email}
        client.post("/admin/password_reset/", data)
        url = re.findall(r"/admin/~reset/.*", mail.outbox[0].body)[0]
        url = client.get(url).url
        response = client.post(
            url, {"new_password1": "1<sdjnsd", "new_password2": "1<sdjnsd"}
        )
        assert response.status_code == 302
        assert response.url == "/admin/login/"
