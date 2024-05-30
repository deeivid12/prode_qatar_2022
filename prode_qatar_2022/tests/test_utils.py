import pytest
import pytz
from datetime import datetime
from commons.tournaments import insert_games_batch, insert_teams_batch
from tournaments.models import Game, Team, Tournament

@pytest.mark.django_db
def test_utils(client):
	path = "/all_games"
	response = client.get(path)
	assert True


@pytest.mark.django_db
def test_insert_teams_batch_success(client):
	teams = [
		{"name": "Argentina", "fifa_code": "ARG"},
		{"name": "Brasil", "fifa_code": "BRA"}
	]
	teams_before_inserts = Team.objects.all()

	assert not teams_before_inserts
	insert_teams_batch(teams)

	teams_after_inserts = Team.objects.all()
	assert teams_after_inserts
	for inserted_team, team in zip(teams_after_inserts, teams):
		assert inserted_team.name == team.get("name")
		assert inserted_team.fifa_code == team.get("fifa_code")

@pytest.mark.django_db
def test_insert_games_batch_success(client):
	teams = [
		{"name": "Argentina", "fifa_code": "ARG"},
		{"name": "Brasil", "fifa_code": "BRA"}
	]
	insert_teams_batch(teams)
	tournament = Tournament(name="Copa America")
	tournament.save()

	games = [
		{"home_team": "Argentina",
		 "away_team": "Brasil",
		 "tournament": "Copa America",
		 "date_time": datetime.now()
   		},
		{"home_team": "Brasil",
		 "away_team": "Argentina",
		 "tournament": "Copa America",
		 "date_time": datetime.now()
   		}
	]

	games_before_inserts = Game.objects.all()

	assert not games_before_inserts
	insert_games_batch(games)
	
	games_after_inserts = Game.objects.all()
	assert games_after_inserts
	for inserted_game, game in zip(games_after_inserts, games):
		assert inserted_game.home_team.name == game.get("home_team")
		assert inserted_game.away_team.name == game.get("away_team")
		assert inserted_game.tournament.name == game.get("tournament")
		assert inserted_game.date_time == game.get("date_time").astimezone(pytz.utc)
