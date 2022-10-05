from tournaments.models import Game, Pronostic
from tournaments.forms import TeamForm, TournamentForm, GameForm, PronosticForm
from commons.tournaments import (
    get_all_pronostics_by_user_and_room,
    update_pronostic,
    new_pronostic_by_form,
    get_do_pronostic_data,
    check_pronostics_results,
    get_ranking_by_room,
)
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse


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
    games = Game.objects.all()
    data = {"games": games, "title": "Todos los partidos"}
    return render(request, "tournaments/games_list.html", data)


def do_pronostic(request, room_id):
    # need to be authenticated, otherwise it won't work
    current_user = request.user
    room = current_user.tournaments_rooms.filter(id=room_id).first()
    if request.method == "POST":
        num_games = Game.objects.filter(tournament_id=room.tournament_id).count()
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
            if pronostic and pronostic.checked:
                break
            if pronostic:
                update_pronostic(pronostic, pronostic_data)
            else:
                new_pronostic_by_form(pronostic_data)
        return redirect("do_pronostic", room_id=room_id)
    else:
        pronostics = get_all_pronostics_by_user_and_room(current_user, room)
        forms = [PronosticForm(instance=pronostic) for pronostic in pronostics]
        # forms and games have the same size
        data = {
            "forms_pronostics": zip(forms, pronostics),
            "title": "Realizar Pronosticos",
        }
        return render(request, "tournaments/do_pronostic.html", data)


def check_pronostics(request):
    check_pronostics_results()
    return redirect("all_games")


def get_points(request):
    # it'll work just for now, to test everything is good
    pronostics = Pronostic.objects.filter(checked=True)
    points = [pronostic.points for pronostic in pronostics]
    print(sum(points))
    return redirect("all_games")


def get_ranking(request, room_id):
    current_user = request.user
    user_rooms_ids = (
        User.objects.filter(id=current_user.id)
        .first()
        .tournaments_rooms.values_list("id", flat=True)
    )
    if room_id not in user_rooms_ids:
        return JsonResponse({"error_404": "No corresponde el room con el usuario"})
    ranking = get_ranking_by_room(room_id)
    data = {"pronostics_ranking": ranking}
    return render(request, "tournaments/pronostics_ranking.html", data)


def get_rooms_list_by_user(request):
    current_user = request.user
    rooms = current_user.tournaments_rooms.all()
    data = {"rooms": rooms}
    return render(request, "tournaments/rooms_list.html", data)


def get_room(request, id):
    current_user = request.user
    room = current_user.tournaments_rooms.filter(id=id).first()
    data = {"room": room}
    return render(request, "tournaments/room_detail.html", data)
