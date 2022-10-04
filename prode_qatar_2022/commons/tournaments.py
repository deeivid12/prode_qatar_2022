from tournaments.forms import PronosticForm
from tournaments.models import Game, Pronostic
from commons.utils import querydict_to_dict


def get_penalties_win(form_data):
	all_values = [{k[-1]: v} for k,v in form_data.items() if k.startswith("ko_win_")]
	penalties = []
	for game_id in form_data.get("pronostic_game"):
		for value in all_values:
			if game_id in value:
				penalties.append(value.get(game_id))
				break
			else:
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


def get_all_pronostics_by_user_and_room(user, room):
	"""Get all pronostics for an user, a room and a tournament_id given.

	Args:
		user (User model instance): User model instance with important information
		room (Room model instance): Room model instance with important information

	Returns:
		list: List of pronostics
	"""
	games = Game.objects.filter(tournament_id=room.tournament_id)
	pronostics = []
	for game in games:
		pronostic = Pronostic.objects.filter(game_id=game.id, user_id=user.id, room_id=room.id).first()
		if not pronostic:
			pronostic = Pronostic(game=game, user=user, room=room)
		pronostics.append(pronostic)
	return pronostics

				
def update_pronostic(pronostic, pronostic_data):
	"""Update pronostic instance (Pronostic model) with provided data

	Args:
		pronostic (Pronostic model instance): Pronostic model instance
		pronostic_data (dict): Provided data like home_goals, away_goals, etc, to update the pronostic
	"""
	pronostic.home_goals = pronostic_data.get("home_goals")
	pronostic.away_goals = pronostic_data.get("away_goals")
	if pronostic.game.is_knockout:
		pronostic.penalties_win = pronostic_data.get("penalties_win")
	pronostic.save()

def new_pronostic_by_form(pronostic_data):
	"""Creates a new pronostic instance by a form and provided data

	Args:
		pronostic_data (dict): Provided data like home_goals, away_goals, etc, to update the pronostic
	"""
	form = PronosticForm(pronostic_data)
	if form.is_valid():
		form.save()
	else:
		print(form.errors.as_data())
