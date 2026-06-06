import os
from datetime import date, datetime, timedelta

from django.utils import timezone

from tournaments.models import Game

DEFAULT_WORLD_CUP_START_DATE = "2026-06-11"
DEFAULT_WORLD_CUP_END_DATE = "2026-07-19"


def _pre_kickoff_minutes() -> int:
    return int(os.environ.get("MINUTES_BEFORE_GAME", 30))


def _post_kickoff_minutes() -> int:
    return int(os.environ.get("MATCH_WINDOW_AFTER_KICKOFF", 150))


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def is_within_tournament_dates(now=None) -> bool:
    """Chequeo barato por calendario del torneo, sin consultar la DB."""
    if now is None:
        now = timezone.now()
    today = timezone.localtime(now).date()
    start = _parse_date(
        os.environ.get("WORLD_CUP_START_DATE", DEFAULT_WORLD_CUP_START_DATE)
    )
    end = _parse_date(
        os.environ.get("WORLD_CUP_END_DATE", DEFAULT_WORLD_CUP_END_DATE)
    )
    return start <= today <= end


def get_active_games(tournament_id=None):
    """Partidos en ventana activa: desde pre-kickoff hasta post-kickoff."""
    now = timezone.now()
    if not is_within_tournament_dates(now):
        return Game.objects.none()

    pre_kickoff = timedelta(minutes=_pre_kickoff_minutes())
    post_kickoff = timedelta(minutes=_post_kickoff_minutes())

    qs = Game.objects.filter(
        date_time__gte=now - post_kickoff,
        date_time__lte=now + pre_kickoff,
    )
    if tournament_id is not None:
        qs = qs.filter(tournament_id=tournament_id)
    return qs


def has_active_matches(tournament_id=None) -> bool:
    return get_active_games(tournament_id).exists()
