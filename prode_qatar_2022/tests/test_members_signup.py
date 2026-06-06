import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse

SIGNUP_URL = reverse("account_signup")
LOGIN_URL = reverse("account_login")
PASSWORD = "secret123"


def signup(client, username):
    return client.post(
        SIGNUP_URL,
        {
            "username": username,
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )


@pytest.mark.django_db
def test_signup_stores_username_in_lowercase(client):
    response = signup(client, "UserName")
    assert response.status_code == 302
    assert User.objects.filter(username="username").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("username", ["admin", "Admin", "ADMIN"])
def test_signup_rejects_reserved_username(client, username):
    response = signup(client, username)
    assert response.status_code == 200
    assert not User.objects.filter(username__iexact="admin").exists()
    assert "Este nombre de usuario no está permitido." in response.content.decode()


@pytest.mark.django_db
@override_settings(RESERVED_USERNAMES={"superuser"})
def test_signup_rejects_usernames_from_settings(client):
    response = signup(client, "superuser")
    assert response.status_code == 200
    assert not User.objects.filter(username="superuser").exists()
    assert "Este nombre de usuario no está permitido." in response.content.decode()


@pytest.mark.django_db
def test_signup_rejects_duplicate_username_case_insensitive(client):
    signup(client, "PlayerOne")
    client.logout()
    response = signup(client, "playerone")
    assert response.status_code == 200
    assert User.objects.filter(username__iexact="playerone").count() == 1


@pytest.mark.django_db
def test_login_is_case_insensitive(client):
    signup(client, "MyUser")
    client.logout()
    response = client.post(
        LOGIN_URL,
        {"login": "MYUSER", "password": PASSWORD},
    )
    assert response.status_code == 302
