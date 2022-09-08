from django.contrib import admin
from tournaments import models

admin.site.register(models.Tournament)
admin.site.register(models.Team)
admin.site.register(models.Game)
admin.site.register(models.Pronostic)
