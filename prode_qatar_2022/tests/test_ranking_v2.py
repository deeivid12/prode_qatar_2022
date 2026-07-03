import pytest
from django.contrib.auth.models import User

from commons.tournaments import build_room_ranking_v2
from tournaments.models import Game, Pronostic, Room, Team, Tournament


@pytest.fixture
def ranking_room(db):
    tournament = Tournament.objects.create(name="Ranking Test", qty_teams=4)
    home = Team.objects.create(name="Home", fifa_code="HOM")
    away = Team.objects.create(name="Away", fifa_code="AWY")
    played = Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time="2026-07-01T19:00:00Z",
        home_goals=2,
        away_goals=1,
        played=True,
    )
    future = Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time="2026-07-10T19:00:00Z",
        played=False,
    )
    room = Room.objects.create(
        name="Sala Test",
        tournament=tournament,
        grand_prize="Premio",
    )
    leader = User.objects.create_user(username="leader", password="pass")
    second = User.objects.create_user(username="second", password="pass")
    empty = User.objects.create_user(username="empty", password="pass")
    room.users.add(leader, second, empty)

    Pronostic.objects.create(
        game=played,
        user=leader,
        home_goals=2,
        away_goals=1,
        checked=True,
        points=5,
    )
    Pronostic.objects.create(
        game=played,
        user=second,
        home_goals=3,
        away_goals=2,
        checked=True,
        points=3,
    )
    Pronostic.objects.create(
        game=future,
        user=leader,
        home_goals=1,
        away_goals=0,
        checked=False,
        points=None,
    )
    return room, leader, second, empty


@pytest.fixture
def ranking_room_client(client, ranking_room):
    _, leader, _, _ = ranking_room
    client.login(username=leader.username, password="pass")
    return client


@pytest.mark.django_db
def test_build_room_ranking_v2_orders_by_points(ranking_room):
    room, leader, second, empty = ranking_room

    ranking = build_room_ranking_v2(room)

    assert [row["username"] for row in ranking] == ["leader", "second", "empty"]
    assert ranking[0] == {
        "position": 1,
        "username": "leader",
        "total": 5,
        "exact_result": 1,
        "partial_result": 0,
    }
    assert ranking[1]["total"] == 3
    assert ranking[1]["partial_result"] == 1
    assert ranking[2]["total"] == 0


@pytest.mark.django_db
def test_build_room_ranking_v2_ignores_unchecked_pronostics(ranking_room):
    room, leader, *_ = ranking_room

    ranking = build_room_ranking_v2(room)
    leader_row = next(r for r in ranking if r["username"] == "leader")

    assert leader_row["total"] == 5


@pytest.mark.django_db
def test_get_ranking_v2_view(ranking_room_client, ranking_room):
    room, *_ = ranking_room

    response = ranking_room_client.get(f"/all_rooms/{room.id}/ranking")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Leader" in content or "leader" in content
    assert "Empty" in content or "empty" in content
