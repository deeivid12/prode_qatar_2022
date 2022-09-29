# Constants

POINTS_CORRECT_SAME_RESULT = 5
POINTS_CORRECT_DIFF_RESULT = 3
POINTS_INCORRECT_RESULT = 0

def querydict_to_dict(query_dict):
	return {k: v[0] if len(v) == 1 else v for k, v in query_dict.lists()}


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


def get_do_pronostic_data(query_dict):
	data = querydict_to_dict(query_dict)
	penalties_data = get_penalties_win(data)
	data["penalties_win"] = penalties_data
	return data




def is_correct_same_result(pronostic, game):
	if (pronostic.home_goals, pronostic.away_goals) == (game.home_goals, game.away_goals):
		return True


def is_correct_different_result(pronostic, game):
	if (pronostic.home_goals > pronostic.away_goals) and (game.home_goals > game.away_goals):
		return True
	elif (pronostic.home_goals < pronostic.away_goals) and (game.home_goals < game.away_goals):
		return True
	elif (pronostic.home_goals == pronostic.away_goals) and (game.home_goals == game.away_goals):
		return True
