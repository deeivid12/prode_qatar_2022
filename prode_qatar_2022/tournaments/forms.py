from django import forms
from tournaments.models import Team, Tournament, Game, Pronostic


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "qty_teams": forms.NumberInput(attrs={"class": "form-control"}),
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        exclude = ["home_goals", "away_goals"]
        widgets = {
            "home_team": forms.TextInput(attrs={"class": "form-control"}),
            "away_team": forms.TextInput(attrs={"class": "form-control"}),
            "tournament": forms.Select(attrs={"class": "form-control"}),
        }


class PronosticForm(forms.ModelForm):
    class Meta:
        model = Pronostic
        fields = "__all__"
        widgets = {
            "home_goals": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "oninput": "check_tie(this)",
                }
            ),
            "away_goals": forms.NumberInput(attrs={"class": "form-control", "oninput": "check_tie(this)",}),
        }
