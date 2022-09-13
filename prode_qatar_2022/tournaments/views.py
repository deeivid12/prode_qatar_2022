from django.shortcuts import render, redirect
from tournaments.models import Game, Pronostic
from tournaments.forms import TeamForm, TournamentForm, GameForm, PronosticForm
from commons.utils import querydict_to_dict


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
	return render(request, "tournaments/games_list.html",
            data)


def do_pronostic(request):
	if request.method == "POST":
		num_games = Game.objects.all().count()
		form_data = querydict_to_dict(request.POST)
		for num in range(num_games):
			pronostic_data = {"game": int(form_data.get("pronostic_game")[num]),"home_goals": int(form_data.get("home_goals")[num]), "away_goals": int(form_data.get("away_goals")[num])}
			pronostic = Pronostic.objects.filter(game_id=pronostic_data.get("game")).first()
			if pronostic:
				pronostic.home_goals = pronostic_data.get("home_goals")
				pronostic.away_goals = pronostic_data.get("away_goals")
				pronostic.save()
			else:
				form = PronosticForm(pronostic_data)
				if form.is_valid():
					form.save()
				else:
					print(form.errors.as_data())
		return redirect("do_pronostic")
	else:
		games = Game.objects.all()
		pronostics = []
		for game in games:
			pronostic = Pronostic.objects.filter(game_id=game.id).first()
			if not pronostic:
				pronostic = Pronostic(game=game)
			pronostics.append(pronostic)
		forms = [PronosticForm(instance=pronostic) for pronostic in pronostics]
		# forms and games have the same size
		data = {"forms_pronostics": zip(forms, pronostics), "title": "Realizar Pronosticos"}
		return render(request, "tournaments/do_pronostic.html",
				data)
