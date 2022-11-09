import pytest
from django.contrib.auth.models import User
from tournaments import views
from tournaments.models import Room, Tournament, Team, Game

USERNAME = PASSWORD = "testuser"


def prepare_data(user):
    tournament = Tournament(
        name="Tournament Test",
    )
    tournament.save()
    room = Room(
        name="Room Test",
        tournament=tournament,
        grand_prize="Test",
    )
    room.save()
    room.users.add(user)
    home_team = Team(name="Test1")
    home_team.save()
    away_team = Team(name="Test2")
    away_team.save()
    game = Game(home_team=home_team, away_team=away_team, tournament=tournament)
    game.save()


@pytest.fixture()
def base_user():
    user = User.objects.create(username=USERNAME)
    user.set_password(PASSWORD)
    user.is_staff = False
    user.save()
    prepare_data(user)
    return user


@pytest.fixture()
def common_user_authenticated_client(client, base_user):
    client.login(username=USERNAME, password=PASSWORD)
    yield client


@pytest.fixture()
def staff_user_authenticated_client(client, base_user):
    base_user.is_staff = True
    base_user.save()
    client.login(username=USERNAME, password=PASSWORD)
    yield client


@pytest.mark.parametrize(
    "path",
    [
        ("/all_rooms"),
        ("/all_rooms/1"),
        ("/all_rooms/1/do_pronostic"),
        ("/all_rooms/1/ranking"),
    ],
)
@pytest.mark.django_db
def test_views_need_authentication(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login")


def test_views_no_need_authentication(client):
    pass


@pytest.mark.parametrize(
    "path",
    [
        ("/check_pronostics"),
    ],
)
@pytest.mark.django_db
def test_views_need_staff_auth_correct_staff_user(
    staff_user_authenticated_client, path
):
    response = staff_user_authenticated_client.get(path)
    assert response.status_code == 302
    assert response.url == "/all_games"


@pytest.mark.parametrize(
    "path",
    [
        ("/check_pronostics"),
    ],
)
@pytest.mark.django_db
def test_views_need_staff_auth_incorrect_staff_user(
    common_user_authenticated_client, path
):
    response = common_user_authenticated_client.get(path)
    assert response.status_code == 302
    assert response.url.startswith("/admin/login")
    assert "next=/check_pronostics" in response.url


@pytest.mark.parametrize(
    "path, view",
    [
        ("/all_rooms", "get_rooms_list_by_user"),
        ("/all_rooms/1", "get_room"),
        ("/all_rooms/1/do_pronostic", "do_pronostic"),
        ("/all_rooms/1/ranking", "get_ranking"),
    ],
)
@pytest.mark.django_db
def test_views_need_common_user_auth_correct_user(
    common_user_authenticated_client, path, view, monkeypatch
):

    response = common_user_authenticated_client.get(path)
    assert response.status_code == 200
