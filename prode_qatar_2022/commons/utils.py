import string
import secrets

# Constants

POINTS_CORRECT_SAME_RESULT = 5
POINTS_CORRECT_DIFF_RESULT = 3
POINTS_INCORRECT_RESULT = 0


def indexes(iterable, obj):
    return (index for index, elem in enumerate(iterable) if elem == obj)


def is_correct_same_result(pronostic, game):
    result = (pronostic.home_goals, pronostic.away_goals) == (
        game.home_goals,
        game.away_goals,
    )
    if game.is_knockout:
        penalties = game.penalties_win == pronostic.penalties_win
        return result and penalties
    return result


def is_correct_different_result(pronostic, game):
    result = (
        (pronostic.home_goals > pronostic.away_goals)
        and (game.home_goals > game.away_goals)
        or (pronostic.home_goals < pronostic.away_goals)
        and (game.home_goals < game.away_goals)
        or (pronostic.home_goals == pronostic.away_goals)
        and (game.home_goals == game.away_goals)
    )
    if game.is_knockout:
        penalties = game.penalties_win == pronostic.penalties_win
        return result and penalties
    return result


def generate_room_code():
    alphabet = string.ascii_letters + string.digits
    room_code = "".join(secrets.choice(alphabet) for i in range(8)).upper()
    return room_code
