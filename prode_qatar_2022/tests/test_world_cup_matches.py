import json
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from tournaments.models import Game, Pronostic, Team, Tournament
from tournaments.schemas.world_cup import WorldCupMatchesFile, WorldCupScore, WorldCupScoreLine
from tournaments.services.world_cup_matches import (
    load_world_cup_matches_file,
    resolve_match_goals,
    resolve_penalties_win,
    sync_world_cup_matches,
    update_world_cup_results,
)

FIXTURE = Path(__file__).parent / "fixtures" / "partidos_mundial_sample.json"
FINISHED_FIXTURE = (
    Path(__file__).parent / "fixtures" / "partidos_mundial_finished_penalties.json"
)


def test_load_world_cup_matches_file_parses_only_required_fields():
    payload = load_world_cup_matches_file(FIXTURE)
    assert len(payload.matches) == 2

    group_match = payload.matches[0]
    assert group_match.id == 537327
    assert group_match.stage == "GROUP_STAGE"
    assert group_match.group == "GROUP_A"
    assert group_match.homeTeam.id == 769
    assert group_match.homeTeam.tla == "MEX"

    knockout_match = payload.matches[1]
    assert knockout_match.stage == "QUARTER_FINALS"
    assert knockout_match.group is None
    assert knockout_match.homeTeam.id is None
    assert knockout_match.awayTeam.name is None


@pytest.mark.django_db
def test_world_cup_matches_endpoint(client):
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload = WorldCupMatchesFile.model_validate(raw)
    with patch("tournaments.views.fetch_wc_matches", return_value=payload) as mock_fetch:
        response = client.get("/api/world-cup/matches")
    assert response.status_code == 200
    mock_fetch.assert_called_once_with(status=None)
    body = response.json()
    assert body["count"] == 2
    assert body["matches"][0]["homeTeam"]["name"] == "Mexico"
    assert body["matches"][1]["homeTeam"]["id"] is None
    assert "odds" not in body["matches"][0]
    assert "referees" not in body["matches"][0]
    assert "area" not in body["matches"][0]


@pytest.fixture
def world_cup_tournament():
    return Tournament.objects.create(name="Mundial 2026 Test", qty_teams=48)


@pytest.fixture
def world_cup_teams_for_matches():
    Team.objects.create(external_id=769, name="Mexico", fifa_code="MEX")
    Team.objects.create(external_id=774, name="South Africa", fifa_code="RSA")


@pytest.mark.django_db
def test_sync_world_cup_matches_group_stage_only(
    world_cup_tournament, world_cup_teams_for_matches
):
    payload = load_world_cup_matches_file(FIXTURE)
    result = sync_world_cup_matches(
        payload, world_cup_tournament, stage="GROUP_STAGE"
    )

    assert len(result["created"]) == 1
    assert result["skipped_undefined_teams"] == []
    assert Game.objects.count() == 1

    game = Game.objects.get(external_id=537327)
    assert game.home_team.fifa_code == "MEX"
    assert game.game_instance == 0
    assert game.is_knockout is False


@pytest.mark.django_db
def test_sync_world_cup_matches_skips_undefined_teams(
    world_cup_tournament, world_cup_teams_for_matches
):
    payload = load_world_cup_matches_file(FIXTURE)
    result = sync_world_cup_matches(
        payload, world_cup_tournament, stage="QUARTER_FINALS"
    )

    assert result["created"] == []
    assert result["skipped_undefined_teams"] == [537385]
    assert Game.objects.count() == 0


@pytest.mark.django_db
def test_sync_world_cup_matches_is_idempotent(
    world_cup_tournament, world_cup_teams_for_matches
):
    payload = load_world_cup_matches_file(FIXTURE)
    sync_world_cup_matches(payload, world_cup_tournament, stage="GROUP_STAGE")
    result = sync_world_cup_matches(
        payload, world_cup_tournament, stage="GROUP_STAGE"
    )

    assert Game.objects.count() == 1
    assert result["created"] == []
    assert len(result["updated"]) == 1


@pytest.mark.django_db
def test_sync_world_cup_matches_skips_missing_team_in_db(world_cup_tournament):
    payload = load_world_cup_matches_file(FIXTURE)
    result = sync_world_cup_matches(
        payload, world_cup_tournament, stage="GROUP_STAGE"
    )

    assert result["created"] == []
    assert len(result["skipped_missing_team"]) == 1


def test_resolve_penalties_win_from_shootout():
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    match = payload.matches[0]
    assert resolve_penalties_win(match.score) == 1


def test_resolve_penalties_win_regular_match_is_zero():
    score = WorldCupScore(
        winner="HOME_TEAM",
        duration="REGULAR",
        fullTime=WorldCupScoreLine(home=3, away=2),
    )
    assert resolve_penalties_win(score) == 0


def test_resolve_match_goals_extra_time():
    score = WorldCupScore(
        winner="HOME_TEAM",
        duration="EXTRA_TIME",
        fullTime=WorldCupScoreLine(home=1, away=1),
        extraTime=WorldCupScoreLine(home=2, away=1),
    )
    assert resolve_match_goals(score) == (2, 1)


def test_resolve_match_goals_penalty_shootout_uses_extra_time():
    score = WorldCupScore(
        winner="HOME_TEAM",
        duration="PENALTY_SHOOTOUT",
        fullTime=WorldCupScoreLine(home=1, away=1),
        extraTime=WorldCupScoreLine(home=2, away=2),
        penalties=WorldCupScoreLine(home=4, away=3),
    )
    assert resolve_match_goals(score) == (2, 2)


@pytest.mark.django_db
def test_update_world_cup_results_sets_goals_and_penalties(
    world_cup_tournament, world_cup_teams_for_matches
):
    game = Game.objects.create(
        external_id=999001,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-07-01T19:00:00Z",
        is_knockout=True,
        game_instance=1,
        home_goals=0,
        away_goals=0,
        played=False,
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    result = update_world_cup_results(payload)

    assert result["updated_count"] == 1
    game.refresh_from_db()
    assert game.home_goals == 3
    assert game.away_goals == 3
    assert game.played is True
    assert game.penalties_win == 1


@pytest.mark.django_db
def test_update_world_cup_results_checks_pronostics(
    world_cup_tournament, world_cup_teams_for_matches
):
    home = Team.objects.get(external_id=769)
    away = Team.objects.get(external_id=774)
    game = Game.objects.create(
        external_id=999001,
        home_team=home,
        away_team=away,
        tournament=world_cup_tournament,
        date_time="2026-07-01T19:00:00Z",
        is_knockout=True,
        game_instance=1,
    )
    user = User.objects.create_user(username="player", password="pass")
    pronostic = Pronostic.objects.create(
        game=game,
        user=user,
        home_goals=3,
        away_goals=3,
        penalties_win=1,
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    update_world_cup_results(payload)

    pronostic.refresh_from_db()
    assert pronostic.checked is True
    assert pronostic.points == 5


@pytest.mark.django_db
def test_update_world_cup_results_regular_3_2_no_penalties(
    world_cup_tournament, world_cup_teams_for_matches
):
    game = Game.objects.create(
        external_id=999003,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-07-03T19:00:00Z",
        played=False,
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    update_world_cup_results(payload)

    game.refresh_from_db()
    assert game.home_goals == 3
    assert game.away_goals == 2
    assert game.penalties_win == 0


@pytest.mark.django_db
def test_update_world_cup_results_extra_time_score(
    world_cup_tournament, world_cup_teams_for_matches
):
    game = Game.objects.create(
        external_id=999004,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-07-04T19:00:00Z",
        is_knockout=True,
        game_instance=1,
        played=False,
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    update_world_cup_results(payload)

    game.refresh_from_db()
    assert game.home_goals == 2
    assert game.away_goals == 1
    assert game.penalties_win == 0


@pytest.mark.django_db
def test_update_world_cup_results_respects_locked_game(
    world_cup_tournament, world_cup_teams_for_matches
):
    game = Game.objects.create(
        external_id=999003,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-07-03T19:00:00Z",
        home_goals=0,
        away_goals=0,
        result_locked=True,
        result_locked_reason="Dato manual validado",
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    result = update_world_cup_results(payload)

    game.refresh_from_db()
    assert game.home_goals == 0
    assert game.away_goals == 0
    assert game.played is False
    assert 999003 in result["skipped_locked"]


@pytest.mark.django_db
def test_update_world_cup_results_skips_non_finished(
    world_cup_tournament, world_cup_teams_for_matches
):
    Game.objects.create(
        external_id=999002,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-06-11T19:00:00Z",
        played=False,
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    result = update_world_cup_results(payload)

    assert result["updated_count"] == 0
    game = Game.objects.get(external_id=999002)
    assert game.played is False


@pytest.mark.django_db
def test_update_world_cup_results_command_from_json(
    world_cup_tournament, world_cup_teams_for_matches
):
    from django.core.management import call_command
    from io import StringIO

    game = Game.objects.create(
        external_id=999003,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-07-03T19:00:00Z",
        played=False,
    )
    out = StringIO()

    call_command(
        "update_world_cup_results",
        f"--from-json={FINISHED_FIXTURE}",
        stdout=out,
    )

    game.refresh_from_db()
    assert game.home_goals == 3
    assert game.away_goals == 2
    assert game.played is True
    assert "Actualizados" in out.getvalue()
    assert "JSON" in out.getvalue()


@pytest.mark.django_db
def test_update_world_cup_results_command_uses_api_by_default(
    world_cup_tournament, world_cup_teams_for_matches
):
    from django.core.management import call_command
    from io import StringIO

    Game.objects.create(
        external_id=999003,
        home_team_id=Team.objects.get(external_id=769).id,
        away_team_id=Team.objects.get(external_id=774).id,
        tournament=world_cup_tournament,
        date_time="2026-07-03T19:00:00Z",
        played=False,
    )
    payload = load_world_cup_matches_file(FINISHED_FIXTURE)
    out = StringIO()

    with patch(
        "tournaments.management.commands.update_world_cup_results.load_wc_matches_payload",
        return_value=payload,
    ) as mock_load:
        call_command("update_world_cup_results", stdout=out)

    mock_load.assert_called_once_with(status="FINISHED")
    assert "API (FINISHED)" in out.getvalue()
