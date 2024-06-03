import os
from tournaments.forms import PronosticForm
from tournaments.models import Game, Pronostic, Room, Team, Tournament
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from commons.utils import (
    querydict_to_dict,
    is_correct_same_result,
    is_correct_different_result,
    POINTS_CORRECT_SAME_RESULT,
    POINTS_CORRECT_DIFF_RESULT,
    POINTS_INCORRECT_RESULT,
)
from datetime import timedelta


def get_penalties_win(form_data):
    """It takes 'penalties win' data from form and it converts it the way
    you can have a list with this information

    Args:
        form_data (dict): Data from form

    Returns:
        list: List with penalties win data
    """
    all_values = [
        {k[7:]: v[0]} for k, v in form_data.items() if k.startswith("ko_win_")
    ]
    penalties = [] if all_values else ["0"] * len(form_data.get("pronostic_game"))
    if penalties:
        return penalties
    for game_id in form_data.get("pronostic_game"):
        was_found = False
        for value_dict in all_values:
            if value_dict.get(game_id):
                penalties.append(value_dict.get(game_id))
                was_found = True
                break
        if not was_found:
            penalties.append("0")
    return penalties


def get_do_pronostic_data(request_data):
    """It takes sent data and it processes it to return it clean and ready to work

    Args:
            request_data (query dict dictionary): Request data from POST

    Returns:
            dict: Clean and ready data to work
    """
    data = querydict_to_dict(request_data)
    penalties_data = get_penalties_win(data)
    data["penalties_win"] = penalties_data
    return data


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
        print(form.errors.as_data())


def check_pronostics_results():
    """Check pronostics versus games results and it updates status and pronostics points"""
    pronostics = Pronostic.objects.filter(checked=False)
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
        users = Room.objects.filter(id=room_id).first().users.all()
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
        print(f"Error al insertar lote de teams: {exc}")
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
        print(f"Error al insertar lote de games: {exc}")
        raise Exception(exc)
