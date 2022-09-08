from django.db import models

class Tournament(models.Model):
	name = models.CharField(max_length=32)
	qty_teams = models.PositiveSmallIntegerField(default=20)

	def __str__(self):
		return f"{self.name}"


class Team(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class Game(models.Model):
	home_team = models.ForeignKey(Team, null=False, related_name="home_team", on_delete=models.CASCADE)
	away_team = models.ForeignKey(Team, null=False, related_name="away_team", on_delete=models.CASCADE)
	home_goals = models.PositiveSmallIntegerField(default=0)
	away_goals = models.PositiveSmallIntegerField(default=0)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.home_team} vs {self.away_team} - {self.tournament}"


class Pronostic(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	home_goals = models.PositiveSmallIntegerField(default=0)
	away_goals = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return f"{self.game} ({self.home_goals}-{self.away_goals})"
