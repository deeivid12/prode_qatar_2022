from tournaments.models import Game, Pronostic, Room
from tournaments.forms import (
    TeamForm,
    TournamentForm,
    GameForm,
    PronosticForm,
    RoomForm,
)
from commons.tournaments import (
    get_all_pronostics_by_user_and_room,
    update_pronostic,
    new_pronostic_by_form,
    get_do_pronostic_data,
    check_pronostics_results,
    get_ranking_by_room,
    is_pronostic_in_time,
)
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
        num_games = Game.objects.filter(
            tournament_id=room.tournament_id, played=False
        ).count()
        form_data = get_do_pronostic_data(request.POST)
        for num in range(num_games):
            pronostic_data = {
                "game": int(form_data.get("pronostic_game")[num]),
                "home_goals": int(form_data.get("home_goals")[num]),
                "away_goals": int(form_data.get("away_goals")[num]),
                "penalties_win": int(form_data.get("penalties_win")[num]),
                "user": current_user,
                "room": room,
            }
            pronostic = Pronostic.objects.filter(
                game_id=pronostic_data.get("game"),
                user_id=current_user.id,
                room_id=room_id,
            ).first()
            # enviar mensaje de error en dicho caso
            if pronostic and pronostic.game.played:
                game_already_played = True
                continue
            if pronostic and pronostic.checked:
                game_already_played = True
                continue
            if pronostic and not is_pronostic_in_time(pronostic.game.date_time):
                game_already_played = True
                continue
            if pronostic:
                update_pronostic(pronostic, pronostic_data)
            else:
                new_pronostic_by_form(pronostic_data)
        if game_already_played or not num_games:
            messages.warning(
                request,
                "Hay pronósticos que no se actualizaron porque los partidos ya se jugaron.",
            )
        return redirect("do_pronostic", room_id=room_id)
    else:
        pronostics = get_all_pronostics_by_user_and_room(current_user, room)
        forms = [PronosticForm(instance=pronostic) for pronostic in pronostics]
        # forms and games have the same size
        data = {
            "forms_pronostics": zip(forms, pronostics),
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
def get_ranking(request, room_id):
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
    current_user = request.user
    room = current_user.tournaments_rooms.filter(id=room_id).first()
    if not room:
        messages.error(
            request,
            "Usted no pertenece a esa sala.",
        )
        redirect("welcome")
    start_date = make_aware(datetime(2022, 11, 20), timezone=timezone.utc)
    end_date = timezone.now() - timedelta(hours=1)
    games_to_show = Game.objects.filter(
        date_time__range=(start_date, end_date),
        tournament=room.tournament.id,
    ).all()  # poner tournament
    all_pronostics = []
    for game in games_to_show:
        pronostics_by_game = Pronostic.objects.filter(game=game.id, room=room.id).all()
        all_pronostics.append(pronostics_by_game)
    data = {"games_pronostics": zip(games_to_show, all_pronostics)}
    return render(request, "tournaments/all_results.html", data)
