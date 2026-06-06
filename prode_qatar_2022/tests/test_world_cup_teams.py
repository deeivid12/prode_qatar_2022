from pathlib import Path
from unittest.mock import patch

import json
import pytest
from django.contrib.auth.models import User

from tournaments.models import Team
from tournaments.schemas.world_cup import WorldCupTeamsFile
from tournaments.services.world_cup_teams import (
    load_world_cup_teams_file,
    sync_teams_from_world_cup,
)

FIXTURE = Path(__file__).parent / "fixtures" / "equipos_mundial_sample.json"


def test_load_world_cup_teams_file_parses_only_required_fields():
    payload = load_world_cup_teams_file(FIXTURE)
    assert len(payload.teams) == 2
    assert payload.teams[0].model_dump() == {
        "id": 758,
        "name": "Uruguay",
        "tla": "URY",
    }


@pytest.mark.django_db
def test_sync_teams_from_world_cup_creates_teams():
    payload = load_world_cup_teams_file(FIXTURE)
    result = sync_teams_from_world_cup(payload)

    assert result["count"] == 2
    assert len(result["created"]) == 2
    assert result["updated"] == []
    assert Team.objects.count() == 2

    uruguay = Team.objects.get(external_id=758)
    assert uruguay.name == "Uruguay"
    assert uruguay.fifa_code == "URY"


@pytest.mark.django_db
def test_sync_teams_from_world_cup_is_idempotent():
    payload = load_world_cup_teams_file(FIXTURE)
    sync_teams_from_world_cup(payload)
    result = sync_teams_from_world_cup(payload)

    assert Team.objects.count() == 2
    assert result["created"] == []
    assert len(result["updated"]) == 2


@pytest.mark.django_db
def test_world_cup_teams_endpoint(client):
    raw = json.loads(
        (Path(__file__).parent / "fixtures" / "equipos_mundial_sample.json").read_text(
            encoding="utf-8"
        )
    )
    payload = WorldCupTeamsFile.model_validate(raw)
    with patch("tournaments.views.fetch_wc_teams", return_value=payload):
        response = client.get("/api/world-cup/teams")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert body["teams"][1]["tla"] == "ARG"


@pytest.mark.django_db
def test_world_cup_teams_sync_endpoint_requires_staff(client):
    response = client.post("/api/world-cup/teams/sync")
    assert response.status_code == 302


@pytest.mark.django_db
def test_world_cup_teams_sync_endpoint_creates_teams(client):
    staff = User.objects.create_user(
        username="staff",
        password="pass",
        is_staff=True,
    )
    client.force_login(staff)
    raw = json.loads(
        (Path(__file__).parent / "fixtures" / "equipos_mundial_sample.json").read_text(
            encoding="utf-8"
        )
    )
    payload = WorldCupTeamsFile.model_validate(raw)
    with patch("tournaments.views.fetch_wc_teams", return_value=payload):
        response = client.post("/api/world-cup/teams/sync")

    assert response.status_code == 201
    body = response.json()
    assert body["count"] == 2
    assert len(body["created"]) == 2
    assert Team.objects.filter(external_id=764, fifa_code="ARG").exists()
