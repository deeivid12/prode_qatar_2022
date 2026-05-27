import os
from tournaments.models import Game, Pronostic, Room
from tournaments.forms import (
    TeamForm,
    TournamentForm,
    GameForm,
    RoomForm,
)
from commons.tournaments import (
    get_all_pronostics_by_user,
    update_pronostic,
    new_pronostic_by_form,
    check_pronostics_results,
    get_ranking_by_room,
    is_pronostic_in_time,
    insert_games_batch,
    insert_teams_batch
)
from commons.bullk_creation import bulk_teams, bulk_games
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, F, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta


@staff_member_required
def new_tournament(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("new_tournament")
    else:
        form = TournamentForm()
        data = {"form": form, "title": "Tournament"}
    return render(request, "tournaments/new.html", data)


@staff_member_required
def new_team(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("new_team")
    else:
        form = TeamForm()
        data = {"form": form, "title": "Team"}
    return render(request, "tournaments/new.html", data)


@staff_member_required
def new_room(request):
    current_user = request.user
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            room.users.set([current_user])
            room.save()
            messages.success(
                request,
                "Se ha registrado la sala correctamente.",
            )
            return redirect("all_rooms")
        else:
            print(form.errors.as_data())
    else:
        form = RoomForm()
        data = {"form": form, "title": "Room"}
    return render(request, "tournaments/new.html", data)


@staff_member_required
def new_game(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("new_game")
    else:
        form = GameForm()
        data = {"form": form, "title": "Game"}
    return render(request, "tournaments/new.html", data)


def get_games_list(request):
    games = Game.objects.order_by("date_time").all()
    data = {"games": games, "title": "Todos los partidos"}
    return render(request, "tournaments/games_list.html", data)


@login_required(login_url="login")
def do_pronostic(request, room_id):
    # need to be authenticated, otherwise it won't work
    game_already_played = False
    current_user = request.user
    room = current_user.tournaments_rooms.filter(id=room_id).first()
    if request.method == "POST":
        games = Game.objects.filter(
            tournament_id=room.tournament_id, played=False
        )
        had_incomplete = False
        had_knockout_penalties_error = False
        for game in games:
            home_raw = request.POST.get(f"home_goals_{game.id}", "").strip()
            away_raw = request.POST.get(f"away_goals_{game.id}", "").strip()

            if not home_raw and not away_raw:
                continue
            if (home_raw and not away_raw) or (not home_raw and away_raw):
                had_incomplete = True
                continue

            if not is_pronostic_in_time(game.date_time):
                game_already_played = True
                continue

            home_goals = int(home_raw)
            away_goals = int(away_raw)
            penalties_win = int(request.POST.get(f"ko_win_{game.id}", "0"))

            if game.is_knockout:
                if home_goals == away_goals:
                    if penalties_win not in (1, 2):
                        had_knockout_penalties_error = True
                        continue
                else:
                    penalties_win = 0

            pronostic_data = {
                "game": game.id,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "penalties_win": penalties_win,
                "user": current_user,
            }
            pronostic = Pronostic.objects.filter(
                game_id=game.id,
                user_id=current_user.id,
            ).first()
            if pronostic:
                if pronostic.checked:
                    game_already_played = True
                    continue
                update_pronostic(pronostic, pronostic_data)
            else:
                new_pronostic_by_form(pronostic_data)
        if game_already_played or not games.exists():
            messages.warning(
                request,
                "Hay pronósticos que no se actualizaron porque los partidos ya se jugaron.",
            )
        if had_incomplete:
            messages.warning(
                request,
                "Algunos partidos tienen solo un gol cargado. Completá ambos goles o dejá ambos vacíos para no guardar ese pronóstico.",
            )
        if had_knockout_penalties_error:
            messages.warning(
                request,
                "En llaves, si pronosticás empate, elegí el ganador por penales.",
            )
        return redirect("do_pronostic", room_id=room_id)
    else:
        pronostics = get_all_pronostics_by_user(current_user, room)
        data = {
            "pronostics": pronostics,
            "title": "Realizar Pronosticos",
            "room_name": room.name,
            "tournament": room.tournament.name,
            "grand_prize": room.grand_prize,
        }
        return render(request, "tournaments/do_pronostic.html", data)


@staff_member_required
def check_pronostics(request):
    check_pronostics_results()
    return redirect("all_games")


def get_points(request):
    # it'll work just for now, to test everything is good
    pronostics = Pronostic.objects.filter(checked=True)
    points = [pronostic.points for pronostic in pronostics]
    print(sum(points))
    return redirect("all_games")


@login_required(login_url="login")
def get_ranking_2(request, room_id):
    """This is a deprecated function."""

    current_user = request.user
    room = Room.objects.filter(id=room_id).first()
    user_rooms_ids = (
        User.objects.filter(id=current_user.id)
        .first()
        .tournaments_rooms.values_list("id", flat=True)
    )
    if room_id not in user_rooms_ids:
        return JsonResponse({"error_404": "No corresponde el room con el usuario"})
    ranking = get_ranking_by_room(room_id)
    data = {
        "pronostics_ranking": ranking,
        "room_name": room.name,
        "tournament": room.tournament.name,
        "grand_prize": room.grand_prize,
    }
    return render(request, "tournaments/pronostics_ranking.html", data)


@login_required(login_url="login")
def get_ranking(request, room_id):
    current_user = request.user
    user_rooms_ids = (
        User.objects.filter(id=current_user.id)
        .first()
        .tournaments_rooms.values_list("id", flat=True)
    )
    if room_id not in user_rooms_ids:
        return JsonResponse({"error_404": "No corresponde el room con el usuario"})
    ranking = []
    room = Room.objects.filter(id=room_id).first()
    tournament_id = room.tournament.id
    users = room.users.all()
    users_ids = [user.id for user in users]
    pronostics_data = list(
        Pronostic.objects
        .filter(game__tournament_id=tournament_id, user_id__in=users_ids)
        .values(username=F('user__username'))
        .annotate(
            total=Sum('points', default=0),
            exact_result=Count(
            Case(
                When(points=5, then=1),
                output_field=IntegerField()
            )),
            partial_result=Count(
            Case(
                When(points=3, then=1),
                output_field=IntegerField()
            )
        )
        )
    )
    by_username = {row["username"]: row for row in pronostics_data}
    merged = []
    for user in users:
        merged.append(
            by_username.get(
                user.username,
                {
                    "username": user.username,
                    "total": 0,
                    "exact_result": 0,
                    "partial_result": 0,
                },
            )
        )
    merged.sort(
        key=lambda r: (-r["total"], -r["exact_result"], -r["partial_result"])
    )
    ranking = [{"position": idx + 1, **item} for idx, item in enumerate(merged)]
    data = {
        "pronostics_ranking": ranking,
        "room_name": room.name,
        "tournament": room.tournament.name,
        "grand_prize": room.grand_prize,
    }
    return render(request, "tournaments/pronostics_ranking.html", data)


@login_required(login_url="login")
def get_rooms_list_by_user(request):
    current_user = request.user
    rooms = current_user.tournaments_rooms.all()
    data = {"rooms": rooms}
    return render(request, "tournaments/rooms_list.html", data)


@login_required(login_url="login")
def get_room(request, id):
    current_user = request.user
    room = current_user.tournaments_rooms.filter(id=id).first()
    data = {
        "room": room,
        "room_name": room.name,
        "tournament": room.tournament.name,
        "grand_prize": room.grand_prize,
    }
    return render(request, "tournaments/room_detail.html", data)


@login_required(login_url="login")
def welcome(request):
    current_user = request.user
    return render(request, "tournaments/welcome.html")


@login_required(login_url="login")
def join_room(request, room_code):
    current_user = request.user
    room = Room.objects.filter(room_code=room_code).first()
    if room:
        found_user = room.users.filter(id=current_user.id).first()
        if not found_user:
            room.users.add(current_user)
            room.save()
            messages.success(
                request,
                "Se ha unido a la sala correctamente.",
            )
        else:
            messages.warning(
                request,
                "Usted ya participa de esta sala porque se ha unido previamente.",
            )
    else:
        messages.warning(
            request,
            "No se puede unir porque el codigo es incorrecto.",
        )
    return redirect("welcome")


def all_results_by_room(request, room_id):
    MINUTES = int(os.environ.get("MINUTES_BEFORE_GAME", 60))
    START_DATE = str(os.environ.get("START_DATE_TO_SHOW_PREDICTIONS", "2025-01-01"))
    dt_naive = datetime.strptime(START_DATE, "%Y-%m-%d")

    current_user = request.user
    room = current_user.tournaments_rooms.filter(id=room_id).first()
    if not room:
        messages.error(
            request,
            "Usted no pertenece a esa sala.",
        )
        redirect("welcome")
    users = room.users.all()
    users_ids = [user.id for user in users]
    start_date = make_aware(dt_naive, timezone=timezone.utc)
    end_date = timezone.now() + timedelta(minutes=MINUTES-5)
    games_to_show = (
        Game.objects.filter(
            date_time__range=(start_date, end_date),
            tournament=room.tournament.id,
        )
        .order_by("date_time")
        .all()
    )  # poner tournament
    all_pronostics = []
    for game in games_to_show:
        pronostics_by_game = Pronostic.objects.filter(game=game.id, user_id__in=users_ids).all()
        all_pronostics.append(pronostics_by_game)
    data = {"games_pronostics": zip(games_to_show, all_pronostics)}
    return render(request, "tournaments/all_results.html", data)


@staff_member_required
def bulk_creation(request, model):
    options = {"team": insert_teams_batch,
               "game": insert_games_batch}
    bulk_data = {"team": bulk_teams,
                 "game": bulk_games}
    if model not in options or model not in bulk_data:
        return JsonResponse({"error": "No se puede crear con modelo seleccionado."})
    try:
        insert_func = options[model]
        data = bulk_data[model]
        insert_func(data)
    except Exception as exc:
        return JsonResponse({"error": f"No se pudo ejecutar: {exc}"})
    return JsonResponse({"success": "Inserts masivos ejecutados correctamente."})
