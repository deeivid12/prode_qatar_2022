import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tournaments.schemas.world_cup import WorldCupMatchesFile, WorldCupTeamsFile
from tournaments.services.football_data_api import (
    fetch_wc_matches,
    fetch_wc_teams,
    load_wc_matches_payload,
)

TEAMS_FIXTURE = Path(__file__).parent / "fixtures" / "equipos_mundial_sample.json"
MATCHES_FIXTURE = Path(__file__).parent / "fixtures" / "partidos_mundial_sample.json"


def test_fetch_wc_teams_from_api():
    raw = json.loads(TEAMS_FIXTURE.read_text(encoding="utf-8"))
    with patch(
        "tournaments.services.football_data_api.FootballDataClient.get_json",
        return_value=raw,
    ) as mock_get:
        payload = fetch_wc_teams()

    mock_get.assert_called_once_with("/v4/competitions/WC/teams")
    assert len(payload.teams) == 2
    assert payload.teams[0].tla == "URY"


def test_fetch_wc_matches_from_api_without_status():
    raw = json.loads(MATCHES_FIXTURE.read_text(encoding="utf-8"))
    with patch(
        "tournaments.services.football_data_api.FootballDataClient.get_json",
        return_value=raw,
    ) as mock_get:
        payload = fetch_wc_matches()

    mock_get.assert_called_once_with("/v4/competitions/WC/matches", params=None)
    assert len(payload.matches) == 2


def test_fetch_wc_matches_from_api_with_finished_status():
    raw = json.loads(MATCHES_FIXTURE.read_text(encoding="utf-8"))
    with patch(
        "tournaments.services.football_data_api.FootballDataClient.get_json",
        return_value=raw,
    ) as mock_get:
        payload = fetch_wc_matches(status="FINISHED")

    mock_get.assert_called_once_with(
        "/v4/competitions/WC/matches",
        params={"status": "FINISHED"},
    )
    assert len(payload.matches) == 2


def test_fetch_wc_matches_rejects_invalid_status():
    with pytest.raises(ValueError, match="Status inválido"):
        fetch_wc_matches(status="TIMED")


def test_load_wc_matches_payload_from_json():
    payload = load_wc_matches_payload(json_path=MATCHES_FIXTURE)
    assert len(payload.matches) == 2


def test_load_wc_matches_payload_from_api():
    raw = json.loads(MATCHES_FIXTURE.read_text(encoding="utf-8"))
    with patch(
        "tournaments.services.football_data_api.FootballDataClient.get_json",
        return_value=raw,
    ):
        payload = load_wc_matches_payload(status="FINISHED")
    assert len(payload.matches) == 2


@pytest.mark.django_db
def test_world_cup_teams_endpoint_uses_api(client):
    raw = json.loads(TEAMS_FIXTURE.read_text(encoding="utf-8"))
    payload = WorldCupTeamsFile.model_validate(raw)
    with patch("tournaments.views.fetch_wc_teams", return_value=payload):
        response = client.get("/api/world-cup/teams")
    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.django_db
def test_world_cup_matches_endpoint_uses_api(client):
    raw = json.loads(MATCHES_FIXTURE.read_text(encoding="utf-8"))
    payload = WorldCupMatchesFile.model_validate(raw)
    with patch("tournaments.views.fetch_wc_matches", return_value=payload) as mock_fetch:
        response = client.get("/api/world-cup/matches")
    assert response.status_code == 200
    mock_fetch.assert_called_once_with(status=None)
    assert response.json()["count"] == 2


@pytest.mark.django_db
def test_world_cup_matches_endpoint_filters_by_live(client):
    raw = json.loads(MATCHES_FIXTURE.read_text(encoding="utf-8"))
    payload = WorldCupMatchesFile.model_validate(raw)
    with patch("tournaments.views.fetch_wc_matches", return_value=payload) as mock_fetch:
        response = client.get("/api/world-cup/matches?status=LIVE")
    assert response.status_code == 200
    mock_fetch.assert_called_once_with(status="LIVE")
    body = response.json()
    assert body["status"] == "LIVE"
    assert body["count"] == 2


@pytest.mark.django_db
def test_world_cup_matches_endpoint_rejects_invalid_status(client):
    response = client.get("/api/world-cup/matches?status=TIMED")
    assert response.status_code == 400
    assert "Status inválido" in response.json()["error"]
