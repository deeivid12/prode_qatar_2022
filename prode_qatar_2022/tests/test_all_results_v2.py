from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from commons.tournaments import build_room_predictions_v2, get_prediction_window_bounds
from tournaments.models import Game, Pronostic, Room, Team, Tournament


@pytest.fixture(autouse=True)
def stable_prediction_window(monkeypatch):
    monkeypatch.setenv("MINUTES_BEFORE_GAME", "60")
    monkeypatch.setenv("START_DATE_TO_SHOW_PREDICTIONS", "2025-01-01")


@pytest.fixture
def prediction_test_bounds():
    """Rango amplio para tests unitarios (independiente de MINUTES_BEFORE_GAME)."""
    now = timezone.now()
    return now - timedelta(days=1), now + timedelta(days=1)


@pytest.fixture
def predictions_room(db):
    tournament = Tournament.objects.create(name="Predictions Test", qty_teams=4)
    home = Team.objects.create(name="Home", fifa_code="HOM")
    away = Team.objects.create(name="Away", fifa_code="AWY")
    now = timezone.now()
    # Dentro de get_prediction_window_bounds() con MINUTES_BEFORE_GAME=60 (tope ~now+55min)
    in_window = Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time=now + timedelta(minutes=30),
        played=False,
    )
    out_of_window = Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time=now + timedelta(days=30),
        played=False,
    )
    room = Room.objects.create(
        name="Sala Predicciones",
        tournament=tournament,
        grand_prize="Premio",
    )
    member = User.objects.create_user(username="member", password="pass")
    outsider = User.objects.create_user(username="outsider", password="pass")
    room.users.add(member)

    Pronostic.objects.create(
        game=in_window,
        user=member,
        home_goals=2,
        away_goals=1,
    )
    Pronostic.objects.create(
        game=in_window,
        user=outsider,
        home_goals=0,
        away_goals=0,
    )
    Pronostic.objects.create(
        game=out_of_window,
        user=member,
        home_goals=1,
        away_goals=1,
    )
    return room, in_window, out_of_window, member


@pytest.fixture
def predictions_client(client, predictions_room):
    _, _, _, member = predictions_room
    client.login(username=member.username, password="pass")
    return client


@pytest.mark.django_db
def test_build_room_predictions_v2_groups_by_game_and_filters_users(predictions_room):
    room, in_window, out_of_window, member = predictions_room
    start_date, end_date = get_prediction_window_bounds()

    games_pronostics = build_room_predictions_v2(room, start_date, end_date)

    assert len(games_pronostics) == 1
    game, pronostics = games_pronostics[0]
    assert game.id == in_window.id
    assert len(pronostics) == 1
    assert pronostics[0].user_id == member.id
    assert out_of_window.id not in {g.id for g, _ in games_pronostics}


@pytest.mark.django_db
def test_build_room_predictions_v2_empty_game_has_no_pronostics(
    predictions_room, prediction_test_bounds
):
    room, in_window, *_ = predictions_room
    start_date, end_date = prediction_test_bounds
    empty_game = Game.objects.create(
        home_team=in_window.home_team,
        away_team=in_window.away_team,
        tournament=room.tournament,
        date_time=timezone.now() + timedelta(hours=2),
        played=False,
    )

    games_pronostics = build_room_predictions_v2(room, start_date, end_date)
    by_game_id = {game.id: pronostics for game, pronostics in games_pronostics}

    assert empty_game.id in by_game_id
    assert by_game_id[empty_game.id] == []


@pytest.mark.django_db
def test_all_results_v2_view(predictions_client, predictions_room):
    room, in_window, *_ = predictions_room

    response = predictions_client.get(f"/all_rooms/{room.id}/all_results")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Predicciones de los Participantes" in content
    assert in_window.home_team.name in content
    assert "Member" in content or "member" in content
