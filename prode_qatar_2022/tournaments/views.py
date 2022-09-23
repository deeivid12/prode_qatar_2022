from django.shortcuts import render, redirect, reverse
from django.db.models import Count, Sum
from tournaments.models import Game, Pronostic, Room
from tournaments.forms import TeamForm, TournamentForm, GameForm, PronosticForm
from commons.utils import querydict_to_dict, is_correct_same_result, is_correct_different_result, POINTS_CORRECT_SAME_RESULT, POINTS_CORRECT_DIFF_RESULT, POINTS_INCORRECT_RESULT
from django.contrib.auth.models import User

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


def do_pronostic(request, room_id):
	# need to be authenticated, otherwise it won't work
	# the idea is having a list of tournaments_ids...
	current_user = request.user
	room = current_user.tournaments_rooms.filter(id=room_id).first()
	tournament_id = room.tournament_id
	if request.method == "POST":
		num_games = Game.objects.filter(tournament_id=tournament_id).count()
		form_data = querydict_to_dict(request.POST)
		for num in range(num_games):
			pronostic_data = {"game": int(form_data.get("pronostic_game")[num]),"home_goals": int(form_data.get("home_goals")[num]), "away_goals": int(form_data.get("away_goals")[num]), "user":current_user, "room":room}
			pronostic = Pronostic.objects.filter(game_id=pronostic_data.get("game"), user_id=current_user.id, room_id=room_id).first()
			if pronostic and pronostic.checked:
				break
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
		return redirect("do_pronostic", room_id=room_id)
	else:
		games = Game.objects.filter(tournament_id=tournament_id)
		pronostics = []
		for game in games:
			pronostic = Pronostic.objects.filter(game_id=game.id, user_id=current_user.id, room_id=room_id).first()
			if not pronostic:
				pronostic = Pronostic(game=game, user=current_user, room=room)
			pronostics.append(pronostic)
		forms = [PronosticForm(instance=pronostic) for pronostic in pronostics]
		# forms and games have the same size
		data = {"forms_pronostics": zip(forms, pronostics), "title": "Realizar Pronosticos"}
		return render(request, "tournaments/do_pronostic.html",
				data)

def check_pronostics(request):
    # only pronostics with 'checked' in False
	pronostics = Pronostic.objects.filter(checked=False)
	for pronostic in pronostics:
		game = Game.objects.filter(id=pronostic.game.id).first()
		if is_correct_same_result(pronostic, game):
			points = POINTS_CORRECT_SAME_RESULT
		elif is_correct_different_result(pronostic, game):
			points = POINTS_CORRECT_DIFF_RESULT
		else:
			points = POINTS_INCORRECT_RESULT
		pronostic.checked = True
		pronostic.points = points
		pronostic.save()
	return redirect('all_games')


def get_points(request):
	# it'll work just for now, to test everything is good
	pronostics = Pronostic.objects.filter(checked=True)
	points = [pronostic.points for pronostic in pronostics]
	print(sum(points))
	return redirect('all_games')


def get_ranking_by_room(request, room_id):
	# TBD: need to validate room_id corresponds to rooms the user has
	pronostics_ranking = Pronostic.objects.values('user_id').filter(checked=True, room_id=room_id).annotate(total=Sum('points')).order_by('-total')
	ranking = []
	for idx, pronostic in enumerate(pronostics_ranking):
		print(pronostic)
		username = User.objects.filter(id=pronostic.get('user_id')).first().username
		position = idx+1
		ranking.append({'position': position, 'username': username, 'total':pronostic.get('total')})
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
