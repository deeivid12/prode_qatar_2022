"""prode_qatar_2022 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tournaments.views import new_tournament, new_team, new_game, get_games_list, do_pronostic

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('new_tournament', new_tournament, name="new_tournament"),
    path('new_team', new_team, name="new_team"),
    path('new_game', new_game, name="new_game"),
    path('do_pronostic', do_pronostic, name="do_pronostic"),
    path('all_games', get_games_list, name="all_games"),
]
