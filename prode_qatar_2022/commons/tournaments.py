import logging
import os
from tournaments.forms import PronosticForm
from tournaments.models import Game, Pronostic, Room, Team, Tournament
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from commons.utils import (
    is_correct_same_result,
    is_correct_different_result,
    POINTS_CORRECT_SAME_RESULT,
    POINTS_CORRECT_DIFF_RESULT,
    POINTS_INCORRECT_RESULT,
)
from datetime import timedelta

logger = logging.getLogger(__name__)


def get_all_pronostics_by_user(user, room):
    """Get all pronostics for an user, a room and a tournament_id given.

    Args:
            user (User model instance): User model instance with important information
            room (Room model instance): Room model instance with important information

    Returns:
            list: List of pronostics
    """
    games = Game.objects.filter(
        tournament_id=room.tournament_id, played=False
    ).order_by("date_time")
    pronostics = []
    for game in games:
        pronostic = Pronostic.objects.filter(
            game_id=game.id, user_id=user.id
        ).first()
        if not pronostic:
            pronostic = Pronostic(game=game, user=user)
        pronostics.append(pronostic)
    return pronostics


def update_pronostic(pronostic, pronostic_data):
    """Update pronostic instance (Pronostic model) with provided data

    Args:
            pronostic (Pronostic model instance): Pronostic model instance
            pronostic_data (dict): Provided data like home_goals, away_goals, etc, to update the pronostic
    """
    if (
        pronostic.home_goals != pronostic_data.get("home_goals")
        or pronostic.away_goals != pronostic_data.get("away_goals")
        or pronostic.penalties_win != pronostic_data.get("penalties_win")
    ):
        pronostic.home_goals = pronostic_data.get("home_goals")
        pronostic.away_goals = pronostic_data.get("away_goals")
        if pronostic.game.is_knockout:
            pronostic.penalties_win = pronostic_data.get("penalties_win")
        pronostic.last_modified = timezone.now()
        pronostic.save()


def new_pronostic_by_form(pronostic_data):
    """Creates a new pronostic instance by a form and provided data

    Args:
            pronostic_data (dict): Provided data like home_goals, away_goals, etc, to update the pronostic
    """
    form = PronosticForm(pronostic_data)
    if form.is_valid():
        pronostic = form.save(commit=False)
        pronostic.last_modified = timezone.now()
        pronostic.save()
    else:
        logger.warning("new_pronostic_by_form: errores de validación: %s", form.errors.as_data())


def check_pronostics_results():
    """Check pronostics versus games results and it updates status and pronostics points"""
    pronostics = Pronostic.objects.filter(checked=False)
    pending_count = pronostics.count()
    checked_count = 0
    for pronostic in pronostics:
        game = Game.objects.filter(id=pronostic.game.id, played=True).first()
        if not game:
            continue
        if is_correct_same_result(pronostic, game):
            points = POINTS_CORRECT_SAME_RESULT
        elif is_correct_different_result(pronostic, game):
            points = POINTS_CORRECT_DIFF_RESULT
        else:
            points = POINTS_INCORRECT_RESULT
        pronostic.checked = True
        pronostic.points = points
        pronostic.save()
        checked_count += 1

    remaining = Pronostic.objects.filter(checked=False).count()
    logger.info(
        "check_pronostics_results: pending=%s checked=%s remaining=%s",
        pending_count,
        checked_count,
        remaining,
    )


def check_pronostics_results_v2():
    """Check pronostics versus games results (optimized: filter + select_related + bulk_update)."""
    pending_count = Pronostic.objects.filter(checked=False).count()

    pronostics = Pronostic.objects.filter(
        checked=False, game__played=True
    ).select_related("game")

    to_update = []
    for pronostic in pronostics:
        game = pronostic.game
        if is_correct_same_result(pronostic, game):
            points = POINTS_CORRECT_SAME_RESULT
        elif is_correct_different_result(pronostic, game):
            points = POINTS_CORRECT_DIFF_RESULT
        else:
            points = POINTS_INCORRECT_RESULT
        pronostic.checked = True
        pronostic.points = points
        to_update.append(pronostic)

    if to_update:
        Pronostic.objects.bulk_update(to_update, ["checked", "points"])

    checked_count = len(to_update)
    remaining = Pronostic.objects.filter(checked=False).count()
    logger.info(
        "check_pronostics_results_v2: pending=%s checked=%s remaining=%s",
        pending_count,
        checked_count,
        remaining,
    )


def run_check_pronostics_results():
    from django.conf import settings

    if settings.PRONOSTICS_CHECK_VERSION == 2:
        return check_pronostics_results_v2()
    return check_pronostics_results()


def get_ranking_by_room(room_id):
    """Gets ranking of users, for a room id given, in ascending order

    Args:
            room_id (int): Room id to calculate the ranking

    Returns:
            list: List of dicts with the following information: position, username and total
    """
    pronostics_ranking = (
        Pronostic.objects.values("user_id")
        .filter(checked=True, room_id=room_id)
        .annotate(total=Sum("points"))
        .order_by("-total")
    )
    ranking = []
    if len(pronostics_ranking) == 0:
        users = Room.objects.filter(id=room_id).first().participants()
        for idx, user in enumerate(users):
            position = idx + 1
            ranking.append(
                {
                    "position": position,
                    "username": user.username,
                    "total": 0,
                }
            )
        return ranking
    for idx, pronostic in enumerate(pronostics_ranking):
        username = User.objects.filter(id=pronostic.get("user_id")).first().username
        position = idx + 1
        ranking.append(
            {
                "position": position,
                "username": username,
                "total": pronostic.get("total"),
            }
        )
    return ranking


def is_pronostic_in_time(game_datetime):
    MINUTES = int(os.environ.get("MINUTES_BEFORE_GAME", 60))
    return timezone.now().timestamp() < (game_datetime - timedelta(minutes=MINUTES)).timestamp()


def insert_teams_batch(teams_batch):
    try:
        with transaction.atomic():
            for team in teams_batch:
                existing_team = Team.objects.filter(name=team.get("name")).first()
                if existing_team:
                    raise Exception(f"Team {existing_team.name} ya existe en db. Proceso abortado.")
                new_team = Team(**team)
                new_team.save()
        return True
    except Exception as exc:
        logger.exception("Error al insertar lote de teams")
        raise Exception(exc)


def insert_games_batch(games_batch):
    try:
        with transaction.atomic():
            for game in games_batch:
                home_team = Team.objects.filter(name=game.get("home_team")).first()
                away_team = Team.objects.filter(name=game.get("away_team")).first()
                tournament = Tournament.objects.filter(name=game.get("tournament")).first()
                new_game = Game(home_team=home_team,
                                away_team=away_team,
                                tournament=tournament,
                                date_time=game.get("date_time"))
                new_game.save()
        return True
    except Exception as exc:
        logger.exception("Error al insertar lote de games")
        raise Exception(exc)
