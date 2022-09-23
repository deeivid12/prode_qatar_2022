from django.contrib.auth.models import User
from django.db import models

class Tournament(models.Model):
	"""This model represents the tournament itself, that the users can select when
	creating a room tournament. Think of it as the "competition", with the corresponding
	games for it and so on.
	"""
	name = models.CharField(max_length=32)
	qty_teams = models.PositiveSmallIntegerField("Quantity Teams",default=20)
	

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


class Room(models.Model):
	"""This model represents the different "room" tournaments the users can create in order to play with friends.
	"""
	name = models.CharField(max_length=100)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	users = models.ManyToManyField(User, related_name="tournaments_rooms")
	grand_prize = models.CharField(max_length=100)
	private = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.name} - {self.tournament}"

class Pronostic(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	room = models.ForeignKey(Room, on_delete=models.CASCADE)
	home_goals = models.PositiveSmallIntegerField(default=0)
	away_goals = models.PositiveSmallIntegerField(default=0)
	checked = models.BooleanField(default=False)
	info = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
	points = models.PositiveSmallIntegerField(blank=True, null=True, default=None)

	def __str__(self):
		return f"{self.game} ({self.home_goals}-{self.away_goals})"




