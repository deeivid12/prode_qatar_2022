from django.shortcuts import render, redirect
from django.forms import modelform_factory
from tournaments.models import Tournament, Team, Game

TournamentForm = modelform_factory(Tournament, exclude=[])
TeamForm = modelform_factory(Team, exclude=[])
GameForm = modelform_factory(Game, exclude=["home_goals", "away_goals"])


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
