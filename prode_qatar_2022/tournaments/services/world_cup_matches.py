import logging
from pathlib import Path

from django.db import transaction

from commons.tournaments import check_pronostics_results
from tournaments.models import Game, Team, Tournament
from tournaments.schemas.world_cup import WorldCupMatch, WorldCupMatchesFile, WorldCupScore

logger = logging.getLogger(__name__)

STAGE_CHOICES = (
    "ALL",
    "GROUP_STAGE",
    "LAST_32",
    "LAST_16",
    "QUARTER_FINALS",
    "SEMI_FINALS",
    "THIRD_PLACE",
    "FINAL",
)

STAGE_TO_GAME_INSTANCE = {
    "GROUP_STAGE": (0, False),
    "LAST_32": (1, True),
    "LAST_16": (1, True),
    "QUARTER_FINALS": (2, True),
    "SEMI_FINALS": (3, True),
    "THIRD_PLACE": (4, True),
    "FINAL": (4, True),
}

FINISHED_STATUSES = frozenset({"FINISHED", "AWARDED"})
PENALTY_SHOOTOUT_DURATION = "PENALTY_SHOOTOUT"
EXTRA_TIME_DURATION = "EXTRA_TIME"
DURATIONS_WITH_EXTRA_TIME_SCORE = frozenset(
    {EXTRA_TIME_DURATION, PENALTY_SHOOTOUT_DURATION}
)


def load_world_cup_matches_file(path: Path | str) -> WorldCupMatchesFile:
    """Lee y valida el JSON de partidos del mundial."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de partidos: {file_path}")
    return WorldCupMatchesFile.model_validate_json(
        file_path.read_text(encoding="utf-8")
    )


def matches_to_public_payload(matches: list[WorldCupMatch]) -> list[dict]:
    return [match.model_dump(mode="json") for match in matches]


def is_match_teams_defined(match: WorldCupMatch) -> bool:
    return match.homeTeam.id is not None and match.awayTeam.id is not None


def resolve_match_goals(score: WorldCupScore) -> tuple[int, int] | None:
    """Marcador para el prode: extraTime tras 120', fullTime si solo hubo 90'."""
    if score.duration in DURATIONS_WITH_EXTRA_TIME_SCORE and score.extraTime:
        home = score.extraTime.home
        away = score.extraTime.away
        if home is not None and away is not None:
            return home, away

    home = score.fullTime.home
    away = score.fullTime.away
    if home is not None and away is not None:
        return home, away
    return None


def resolve_penalties_win(score: WorldCupScore) -> int:
    """Devuelve penalties_win del Game: 0=ninguno, 1=local, 2=visitante."""
    if score.duration != PENALTY_SHOOTOUT_DURATION:
        return 0

    if score.penalties:
        home = score.penalties.home
        away = score.penalties.away
        if home is not None and away is not None:
            if home > away:
                return 1
            if away > home:
                return 2

    if score.winner == "HOME_TEAM":
        return 1
    if score.winner == "AWAY_TEAM":
        return 2
    return 0


def apply_match_result_to_game(game: Game, match: WorldCupMatch) -> bool:
    """Actualiza goles, played y penales. Retorna True si hubo cambios."""
    goals = resolve_match_goals(match.score)
    if goals is None:
        return False
    home_goals, away_goals = goals

    penalties_win = resolve_penalties_win(match.score)
    new_values = {
        "home_goals": home_goals,
        "away_goals": away_goals,
        "played": True,
        "penalties_win": penalties_win,
    }
    changed = any(getattr(game, field) != value for field, value in new_values.items())
    if not changed:
        return False

    for field, value in new_values.items():
        setattr(game, field, value)
    game.save(update_fields=list(new_values.keys()))
    return True


def update_world_cup_results(payload: WorldCupMatchesFile) -> dict:
    """Actualiza resultados de partidos ya existentes en DB (JSON finalizado)."""
    updated = []
    skipped_not_finished = 0
    skipped_no_score = []
    skipped_not_in_db = []
    skipped_locked = []

    with transaction.atomic():
        for match in payload.matches:
            if match.status not in FINISHED_STATUSES:
                skipped_not_finished += 1
                continue

            goals = resolve_match_goals(match.score)
            if goals is None:
                skipped_no_score.append(match.id)
                continue
            home_goals, away_goals = goals

            game = Game.objects.filter(external_id=match.id).first()
            if not game:
                skipped_not_in_db.append(match.id)
                continue
            if game.result_locked:
                skipped_locked.append(match.id)
                continue

            if apply_match_result_to_game(game, match):
                updated.append(
                    {
                        "external_id": match.id,
                        "home_goals": home_goals,
                        "away_goals": away_goals,
                        "penalties_win": resolve_penalties_win(match.score),
                    }
                )

    check_pronostics_results()

    result = {
        "updated": updated,
        "updated_count": len(updated),
        "skipped_not_finished": skipped_not_finished,
        "skipped_no_score": skipped_no_score,
        "skipped_not_in_db": skipped_not_in_db,
        "skipped_locked": skipped_locked,
    }

    logger.info(
        "update_world_cup_results: updated=%s skipped_not_finished=%s "
        "skipped_no_score=%s skipped_not_in_db=%s skipped_locked=%s",
        result["updated_count"],
        skipped_not_finished,
        len(skipped_no_score),
        len(skipped_not_in_db),
        len(skipped_locked),
    )
    if skipped_no_score:
        logger.warning(
            "update_world_cup_results: partidos FINISHED sin marcador: %s",
            skipped_no_score,
        )
    if skipped_not_in_db:
        logger.warning(
            "update_world_cup_results: partidos no encontrados en DB: %s",
            skipped_not_in_db,
        )
    if skipped_locked:
        logger.warning(
            "update_world_cup_results: partidos omitidos por bloqueo manual: %s",
            skipped_locked,
        )

    return result


def filter_matches_by_stage(
    matches: list[WorldCupMatch], stage: str
) -> list[WorldCupMatch]:
    if stage == "ALL":
        return matches
    return [match for match in matches if match.stage == stage]


def sync_world_cup_matches(
    payload: WorldCupMatchesFile,
    tournament: Tournament,
    stage: str = "ALL",
) -> dict:
    """Crea o actualiza partidos en DB. Omite partidos sin equipos definidos."""
    if stage not in STAGE_CHOICES:
        raise ValueError(f"Stage inválido: {stage}. Opciones: {', '.join(STAGE_CHOICES)}")

    created = []
    updated = []
    skipped_undefined_teams = []
    skipped_missing_team = []
    skipped_unknown_stage = []

    matches = filter_matches_by_stage(payload.matches, stage)

    with transaction.atomic():
        for match in matches:
            if match.stage not in STAGE_TO_GAME_INSTANCE:
                skipped_unknown_stage.append(match.id)
                continue

            if not is_match_teams_defined(match):
                skipped_undefined_teams.append(match.id)
                continue

            home_team = Team.objects.filter(external_id=match.homeTeam.id).first()
            away_team = Team.objects.filter(external_id=match.awayTeam.id).first()

            if not home_team:
                skipped_missing_team.append(
                    {"match_id": match.id, "team_external_id": match.homeTeam.id}
                )
                continue
            if not away_team:
                skipped_missing_team.append(
                    {"match_id": match.id, "team_external_id": match.awayTeam.id}
                )
                continue

            game_instance, is_knockout = STAGE_TO_GAME_INSTANCE[match.stage]
            is_finished = match.status in FINISHED_STATUSES
            goals = resolve_match_goals(match.score) if is_finished else None
            if goals:
                home_goals, away_goals = goals
            else:
                home_goals, away_goals = 0, 0

            game, was_created = Game.objects.update_or_create(
                external_id=match.id,
                defaults={
                    "home_team": home_team,
                    "away_team": away_team,
                    "tournament": tournament,
                    "date_time": match.utcDate,
                    "game_instance": game_instance,
                    "is_knockout": is_knockout,
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "played": is_finished,
                    "penalties_win": (
                        resolve_penalties_win(match.score) if is_finished else 0
                    ),
                },
            )
            entry = {
                "id": game.id,
                "external_id": match.id,
                "home_team": home_team.name,
                "away_team": away_team.name,
                "stage": match.stage,
            }
            if was_created:
                created.append(entry)
            else:
                updated.append(entry)

    result = {
        "stage": stage,
        "processed": len(matches),
        "created": created,
        "updated": updated,
        "skipped_undefined_teams": skipped_undefined_teams,
        "skipped_missing_team": skipped_missing_team,
        "skipped_unknown_stage": skipped_unknown_stage,
    }

    logger.info(
        "sync_world_cup_matches stage=%s processed=%s created=%s updated=%s "
        "skipped_undefined_teams=%s skipped_missing_team=%s skipped_unknown_stage=%s",
        stage,
        result["processed"],
        len(created),
        len(updated),
        len(skipped_undefined_teams),
        len(skipped_missing_team),
        len(skipped_unknown_stage),
    )
    if skipped_missing_team:
        logger.warning(
            "sync_world_cup_matches: equipos no encontrados en DB (ejecutá sync_world_cup_teams): %s",
            skipped_missing_team[:10],
        )
    if skipped_unknown_stage:
        logger.warning(
            "sync_world_cup_matches: stages desconocidos: %s",
            skipped_unknown_stage,
        )

    return result
