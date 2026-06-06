import logging
from pathlib import Path

from pydantic import ValidationError

from tournaments.integrations.football_data_client import FootballDataClient

logger = logging.getLogger(__name__)
from tournaments.schemas.world_cup import WorldCupMatchesFile, WorldCupTeamsFile
from tournaments.services.world_cup_matches import load_world_cup_matches_file

WC_TEAMS_PATH = "/v4/competitions/WC/teams"
WC_MATCHES_PATH = "/v4/competitions/WC/matches"

WC_MATCH_STATUS_CHOICES = frozenset({"LIVE", "FINISHED"})


def fetch_wc_teams() -> WorldCupTeamsFile:
    """Obtiene equipos del Mundial desde football-data.org."""
    raw = FootballDataClient().get_json(WC_TEAMS_PATH)
    try:
        return WorldCupTeamsFile.model_validate(raw)
    except ValidationError as exc:
        logger.error("Respuesta inválida de %s: %s", WC_TEAMS_PATH, exc)
        raise ValueError(f"Respuesta inválida de {WC_TEAMS_PATH}: {exc}") from exc


def fetch_wc_matches(status: str | None = None) -> WorldCupMatchesFile:
    """Obtiene partidos del Mundial desde football-data.org.

    status: opcional, LIVE o FINISHED (query param de football-data.org).
    """
    if status is not None and status not in WC_MATCH_STATUS_CHOICES:
        raise ValueError(
            f"Status inválido: {status}. Opciones: {', '.join(sorted(WC_MATCH_STATUS_CHOICES))}"
        )

    params = {"status": status} if status else None
    raw = FootballDataClient().get_json(WC_MATCHES_PATH, params=params)
    try:
        return WorldCupMatchesFile.model_validate(raw)
    except ValidationError as exc:
        logger.error("Respuesta inválida de %s: %s", WC_MATCHES_PATH, exc)
        raise ValueError(f"Respuesta inválida de {WC_MATCHES_PATH}: {exc}") from exc


def load_wc_matches_payload(
    *,
    status: str | None = None,
    json_path: str | Path | None = None,
) -> WorldCupMatchesFile:
    """Obtiene partidos desde JSON local o desde football-data.org."""
    if json_path is not None:
        path = Path(json_path)
        logger.info("load_wc_matches_payload: leyendo JSON %s", path)
        return load_world_cup_matches_file(path)
    return fetch_wc_matches(status=status)
