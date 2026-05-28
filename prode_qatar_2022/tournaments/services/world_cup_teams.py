from pathlib import Path

from django.db import transaction

from tournaments.models import Team
from tournaments.schemas.world_cup import WorldCupTeam, WorldCupTeamsFile


def load_world_cup_teams_file(path: Path | str) -> WorldCupTeamsFile:
    """Lee y valida el JSON de equipos del mundial."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de equipos: {file_path}")
    return WorldCupTeamsFile.model_validate_json(
        file_path.read_text(encoding="utf-8")
    )


def teams_to_public_payload(teams: list[WorldCupTeam]) -> list[dict]:
    return [team.model_dump() for team in teams]


def _team_sync_entry(team: Team, external_id: int) -> dict:
    return {
        "id": team.id,
        "external_id": external_id,
        "name": team.name,
        "fifa_code": team.fifa_code,
    }


def sync_teams_from_world_cup(payload: WorldCupTeamsFile) -> dict:
    """Crea o actualiza equipos en DB a partir del JSON validado con Pydantic."""
    created = []
    updated = []
    with transaction.atomic():
        for wc_team in payload.teams:
            team, was_created = Team.objects.update_or_create(
                external_id=wc_team.id,
                defaults={
                    "name": wc_team.name,
                    "fifa_code": wc_team.tla,
                },
            )
            entry = _team_sync_entry(team, wc_team.id)
            if was_created:
                created.append(entry)
            else:
                updated.append(entry)
    return {
        "count": len(payload.teams),
        "created": created,
        "updated": updated,
    }
