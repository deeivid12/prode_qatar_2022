from django.contrib import admin
from tournaments import forms, models


class GameAdmin(admin.ModelAdmin):
    form = forms.GameAdminForm

    fieldsets = (
        (None, {
            'fields': ('tournament', 'game_instance', 'date_time')
        }),
        ('Teams', {
            'fields': ('home_team', 'away_team')
        }),
        ('Match Details', {
            'fields': ('is_knockout', 'penalties_win', 'home_goals', 'away_goals', 'played')
        }),
    )

    list_display = (
        'get_game_display',
        'tournament',
        'game_instance',
        'home_team',
        'away_team',
        'is_knockout',
        'penalties_win',
        'date_time',
        'played'
    )

    @admin.display(description='Match')
    def get_game_display(self, obj):
        return str(obj)

admin.site.register(models.Team)
admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Tournament)
admin.site.register(models.Pronostic)
admin.site.register(models.Room)
