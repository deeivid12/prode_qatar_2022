import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from tournaments import views
from tournaments.models import Room, Tournament, Team, Game, Pronostic

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
    game = Game(
        home_team=home_team,
        away_team=away_team,
        tournament=tournament,
        date_time=timezone.now() + timedelta(hours=2),
    )
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


@pytest.mark.django_db
def test_do_pronostic_create_pronostics_with_zero_to_zero_by_default(
    common_user_authenticated_client, base_user
):
    """Si el usuario envía 0 y 0 explícitamente, se persiste el pronóstico 0-0."""
    room = Room.objects.first()
    game = Game.objects.first()
    game.date_time = timezone.now() + timedelta(hours=2)
    game.save()

    payload = {
        f"home_goals_{game.id}": "0",
        f"away_goals_{game.id}": "0",
    }

    resp = common_user_authenticated_client.post(
        f"/all_rooms/{room.id}/do_pronostic", data=payload,
    )

    assert resp.status_code in (200, 302)
    assert Pronostic.objects.filter(user=base_user, game=game).exists()
    p = Pronostic.objects.get(user=base_user, game=game)
    assert p.home_goals == 0
    assert p.away_goals == 0


@pytest.mark.django_db
def test_do_pronostic_skips_when_goal_fields_are_empty(
    common_user_authenticated_client, base_user
):
    """Campos vacíos: no se crea pronóstico."""
    room = Room.objects.first()
    game = Game.objects.first()
    game.date_time = timezone.now() + timedelta(hours=2)
    game.save()

    payload = {
        f"home_goals_{game.id}": "",
        f"away_goals_{game.id}": "",
    }

    resp = common_user_authenticated_client.post(
        f"/all_rooms/{room.id}/do_pronostic", data=payload,
    )

    assert resp.status_code == 302
    assert not Pronostic.objects.filter(user=base_user, game=game).exists()


@pytest.mark.django_db
def test_do_pronostic_skips_when_only_one_goal_field_filled(
    common_user_authenticated_client, base_user
):
    """Solo un gol cargado: no se crea pronóstico."""
    room = Room.objects.first()
    game = Game.objects.first()
    game.date_time = timezone.now() + timedelta(hours=2)
    game.save()

    payload = {
        f"home_goals_{game.id}": "2",
        f"away_goals_{game.id}": "",
    }

    resp = common_user_authenticated_client.post(
        f"/all_rooms/{room.id}/do_pronostic", data=payload,
    )

    assert resp.status_code == 302
    assert not Pronostic.objects.filter(user=base_user, game=game).exists()


@pytest.mark.django_db
def test_do_pronostic_creates_pronostic_with_explicit_goals(
    common_user_authenticated_client, base_user
):
    """Goles explícitos (2-1): se crea el pronóstico con esos valores."""
    room = Room.objects.first()
    game = Game.objects.first()
    game.date_time = timezone.now() + timedelta(hours=2)
    game.save()

    payload = {
        f"home_goals_{game.id}": "2",
        f"away_goals_{game.id}": "1",
    }

    resp = common_user_authenticated_client.post(
        f"/all_rooms/{room.id}/do_pronostic", data=payload,
    )

    assert resp.status_code == 302
    p = Pronostic.objects.get(user=base_user, game=game)
    assert p.home_goals == 2
    assert p.away_goals == 1


@pytest.mark.django_db
def test_do_pronostic_updates_existing_pronostic(
    common_user_authenticated_client, base_user
):
    """Un pronóstico existente se actualiza sin duplicarse."""
    room = Room.objects.first()
    game = Game.objects.first()
    game.date_time = timezone.now() + timedelta(hours=2)
    game.save()

    Pronostic.objects.create(
        game=game, user=base_user, home_goals=1, away_goals=0,
    )

    payload = {
        f"home_goals_{game.id}": "3",
        f"away_goals_{game.id}": "2",
    }

    resp = common_user_authenticated_client.post(
        f"/all_rooms/{room.id}/do_pronostic", data=payload,
    )

    assert resp.status_code == 302
    assert Pronostic.objects.filter(user=base_user, game=game).count() == 1
    p = Pronostic.objects.get(user=base_user, game=game)
    assert p.home_goals == 3
    assert p.away_goals == 2


@pytest.mark.django_db
def test_do_pronostic_does_not_update_played_game(
    common_user_authenticated_client, base_user
):
    """Un partido ya jugado no permite modificar el pronóstico."""
    room = Room.objects.first()
    game = Game.objects.first()
    game.date_time = timezone.now() + timedelta(hours=2)
    game.played = True
    game.home_goals = 1
    game.away_goals = 0
    game.save()

    Pronostic.objects.create(
        game=game, user=base_user, home_goals=0, away_goals=0,
    )

    payload = {
        f"home_goals_{game.id}": "5",
        f"away_goals_{game.id}": "5",
    }

    resp = common_user_authenticated_client.post(
        f"/all_rooms/{room.id}/do_pronostic", data=payload,
    )

    assert resp.status_code == 302
    p = Pronostic.objects.get(user=base_user, game=game)
    assert p.home_goals == 0
    assert p.away_goals == 0


@pytest.mark.django_db
def test_ranking_includes_user_without_pronostics(
    common_user_authenticated_client, base_user
):
    """Un usuario de la sala sin pronósticos aparece en el ranking con total 0."""
    room = Room.objects.first()
    user2 = User.objects.create(username="user_sin_pronosticos")
    user2.set_password("pass")
    user2.save()
    room.users.add(user2)

    resp = common_user_authenticated_client.get(
        f"/all_rooms/{room.id}/ranking",
    )

    assert resp.status_code == 200
    content = resp.content.decode()
    assert "User_Sin_Pronosticos" in content or "user_sin_pronosticos" in content


@pytest.mark.django_db
def test_check_pronostics_does_not_create_points_for_missing_pronostic(
    staff_user_authenticated_client, base_user
):
    """Si no hay pronóstico para un partido jugado, check_pronostics no crea filas fantasma."""
    game = Game.objects.first()
    game.date_time = timezone.now() - timedelta(hours=2)
    game.played = True
    game.home_goals = 1
    game.away_goals = 1
    game.save()

    assert not Pronostic.objects.filter(user=base_user, game=game).exists()

    staff_user_authenticated_client.get("/check_pronostics")

    assert not Pronostic.objects.filter(user=base_user, game=game).exists()
