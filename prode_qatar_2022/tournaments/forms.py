from django import forms
from tournaments.models import Room, Team, Tournament, Game, Pronostic


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ["room_code", "users"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


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
        exclude = ["last_modified"]
        widgets = {
            "home_goals": forms.NumberInput(
                attrs={
                    "class": "form-control border border-dark",
                    "oninput": "check_tie(this)",
                }
            ),
            "away_goals": forms.NumberInput(
                attrs={
                    "class": "form-control border border-dark",
                    "oninput": "check_tie(this)",
                }
            ),
        }


class GameAdminForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'

    home_team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'vTextField'})
    )
    away_team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'vTextField'})
    )
    tournament = forms.ModelChoiceField(
        queryset=Tournament.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'vTextField'})
    )
