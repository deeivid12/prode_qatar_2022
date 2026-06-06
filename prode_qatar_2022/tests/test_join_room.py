import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from tournaments.models import Room, Tournament

PASSWORD = "secret123"
NEW_ROOM_URL = reverse("new_room")


@pytest.fixture
def tournament():
    return Tournament.objects.create(name="Mundial Test")


@pytest.fixture
def player(client):
    user = User.objects.create_user("player", password=PASSWORD)
    client.login(username="player", password=PASSWORD)
    return user


@pytest.fixture
def staff_user(client):
    user = User.objects.create_user("staffuser", password=PASSWORD, is_staff=True)
    client.login(username="staffuser", password=PASSWORD)
    return user


def create_room_payload(tournament, private):
    payload = {
        "name": "Sala Test",
        "tournament": tournament.id,
        "grand_prize": "Premio",
    }
    if private:
        payload["private"] = "on"
    return payload


@pytest.mark.django_db
def test_join_public_room_succeeds(client, tournament, player):
    room = Room.objects.create(
        name="Sala Publica",
        tournament=tournament,
        grand_prize="Premio",
        private=False,
        room_code="PUBLCODE",
    )

    response = client.get(reverse("join_room", args=["PUBLCODE"]))

    assert response.status_code == 302
    assert room.users.filter(id=player.id).exists()


@pytest.mark.django_db
def test_join_private_room_is_rejected(client, tournament, player):
    room = Room.objects.create(
        name="Sala Privada",
        tournament=tournament,
        grand_prize="Premio",
        private=True,
        room_code="PRIVCODE",
    )

    response = client.get(reverse("join_room", args=["PRIVCODE"]))

    assert response.status_code == 302
    assert not room.users.filter(id=player.id).exists()


@pytest.mark.django_db
def test_join_private_room_allows_existing_member(client, tournament):
    room = Room.objects.create(
        name="Sala Privada",
        tournament=tournament,
        grand_prize="Premio",
        private=True,
        room_code="PRIVCODE",
    )
    user = User.objects.create_user("member", password=PASSWORD)
    room.users.add(user)
    client.login(username="member", password=PASSWORD)

    response = client.get(reverse("join_room", args=["PRIVCODE"]))

    assert response.status_code == 302
    assert room.users.filter(id=user.id).exists()


@pytest.mark.django_db
def test_new_private_room_does_not_add_staff(client, tournament, staff_user):
    response = client.post(
        NEW_ROOM_URL,
        create_room_payload(tournament, private=True),
    )

    assert response.status_code == 302
    room = Room.objects.get(name="Sala Test")
    assert room.private is True
    assert not room.users.filter(id=staff_user.id).exists()


@pytest.mark.django_db
def test_new_public_room_adds_staff(client, tournament, staff_user):
    response = client.post(
        NEW_ROOM_URL,
        create_room_payload(tournament, private=False),
    )

    assert response.status_code == 302
    room = Room.objects.get(name="Sala Test")
    assert room.private is False
    assert room.users.filter(id=staff_user.id).exists()


@pytest.mark.django_db
def test_ranking_excludes_staff(client, tournament):
    room = Room.objects.create(
        name="Sala Ranking",
        tournament=tournament,
        grand_prize="Premio",
        private=True,
        room_code="RANKROOM",
    )
    player = User.objects.create_user("player", password=PASSWORD)
    staff = User.objects.create_user("staffplayer", password=PASSWORD, is_staff=True)
    room.users.add(player, staff)
    client.login(username="player", password=PASSWORD)

    response = client.get(reverse("ranking", args=[room.id]))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Player" in content
    assert "Staffplayer" not in content
    assert "staffplayer" not in content
