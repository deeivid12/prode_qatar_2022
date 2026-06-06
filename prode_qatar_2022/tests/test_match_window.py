from datetime import datetime
from unittest.mock import patch

import pytest
from django.utils.timezone import make_aware

from tournaments.models import Game, Team, Tournament
from tournaments.services.match_window import (
    get_active_games,
    has_active_matches,
    is_within_tournament_dates,
)


@pytest.fixture
def world_cup_tournament():
    return Tournament.objects.create(name="Mundial 2026 Test", qty_teams=48)


@pytest.fixture
def world_cup_teams():
    home = Team.objects.create(external_id=769, name="Mexico", fifa_code="MEX")
    away = Team.objects.create(external_id=774, name="South Africa", fifa_code="RSA")
    return home, away


def _create_game(tournament, home, away, kickoff):
    return Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time=kickoff,
    )


@pytest.fixture(autouse=True)
def match_window_env(monkeypatch):
    monkeypatch.setenv("MINUTES_BEFORE_GAME", "30")
    monkeypatch.setenv("MATCH_WINDOW_AFTER_KICKOFF", "150")
    monkeypatch.setenv("WORLD_CUP_START_DATE", "2026-06-11")
    monkeypatch.setenv("WORLD_CUP_END_DATE", "2026-07-19")


def test_is_within_tournament_dates_inside_range():
    now = make_aware(datetime(2026, 6, 15, 12, 0, 0))
    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        assert is_within_tournament_dates() is True


def test_is_within_tournament_dates_outside_range():
    now = make_aware(datetime(2026, 5, 1, 12, 0, 0))
    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        assert is_within_tournament_dates() is False


@pytest.mark.django_db
def test_has_active_matches_before_kickoff(world_cup_tournament, world_cup_teams):
    home, away = world_cup_teams
    kickoff = make_aware(datetime(2026, 6, 11, 19, 0, 0))
    game = _create_game(world_cup_tournament, home, away, kickoff)
    now = make_aware(datetime(2026, 6, 11, 18, 45, 0))

    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        assert has_active_matches(world_cup_tournament.id) is True
        assert list(get_active_games(world_cup_tournament.id)) == [game]


@pytest.mark.django_db
def test_has_active_matches_during_match(world_cup_tournament, world_cup_teams):
    home, away = world_cup_teams
    kickoff = make_aware(datetime(2026, 6, 11, 19, 0, 0))
    _create_game(world_cup_tournament, home, away, kickoff)
    now = make_aware(datetime(2026, 6, 11, 20, 30, 0))

    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        assert has_active_matches(world_cup_tournament.id) is True


@pytest.mark.django_db
def test_has_active_matches_after_window(world_cup_tournament, world_cup_teams):
    home, away = world_cup_teams
    kickoff = make_aware(datetime(2026, 6, 11, 19, 0, 0))
    _create_game(world_cup_tournament, home, away, kickoff)
    now = make_aware(datetime(2026, 6, 11, 22, 0, 0))

    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        assert has_active_matches(world_cup_tournament.id) is False


@pytest.mark.django_db
def test_has_active_matches_before_window(world_cup_tournament, world_cup_teams):
    home, away = world_cup_teams
    kickoff = make_aware(datetime(2026, 6, 11, 19, 0, 0))
    _create_game(world_cup_tournament, home, away, kickoff)
    now = make_aware(datetime(2026, 6, 11, 18, 0, 0))

    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        assert has_active_matches(world_cup_tournament.id) is False


@pytest.mark.django_db
def test_get_active_games_filters_by_tournament(world_cup_tournament, world_cup_teams):
    home, away = world_cup_teams
    other_tournament = Tournament.objects.create(name="Otro torneo", qty_teams=8)
    kickoff = make_aware(datetime(2026, 6, 11, 19, 0, 0))
    active_game = _create_game(world_cup_tournament, home, away, kickoff)
    _create_game(other_tournament, home, away, kickoff)
    now = make_aware(datetime(2026, 6, 11, 18, 45, 0))

    with patch("tournaments.services.match_window.timezone.now", return_value=now):
        active_games = list(get_active_games(world_cup_tournament.id))

    assert active_games == [active_game]


@pytest.mark.django_db
def test_has_active_matches_skips_db_outside_tournament_dates(
    world_cup_tournament, world_cup_teams
):
    home, away = world_cup_teams
    kickoff = make_aware(datetime(2026, 6, 11, 19, 0, 0))
    _create_game(world_cup_tournament, home, away, kickoff)
    now = make_aware(datetime(2026, 5, 1, 12, 0, 0))

    with patch("tournaments.services.match_window.timezone.now", return_value=now), patch(
        "tournaments.services.match_window.Game.objects.filter"
    ) as mock_filter:
        assert has_active_matches(world_cup_tournament.id) is False

    mock_filter.assert_not_called()
