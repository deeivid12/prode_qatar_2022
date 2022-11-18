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
from django.urls import path, include
from tournaments.views import (
    get_rooms_list_by_user,
    get_room,
    new_tournament,
    new_team,
    new_game,
    new_room,
    get_games_list,
    do_pronostic,
    check_pronostics,
    get_points,
    get_ranking,
    welcome,
    join_room,
)

urlpatterns = [
    path("", welcome),
    path("admin/", admin.site.urls, name="admin"),
    path("welcome", welcome, name="welcome"),
    path("new_tournament", new_tournament, name="new_tournament"),
    path("new_team", new_team, name="new_team"),
    path("new_game", new_game, name="new_game"),
    path("new_room", new_room, name="new_room"),
    path("join_room/<room_code>", join_room, name="join_room"),
    # path('do_pronostic', do_pronostic, name="do_pronostic"),
    path("all_games", get_games_list, name="all_games"),
    path("all_rooms", get_rooms_list_by_user, name="all_rooms"),
    path("all_rooms/<int:id>", get_room, name="get_room"),
    path("all_rooms/<int:room_id>/do_pronostic", do_pronostic, name="do_pronostic"),
    path("all_rooms/<int:room_id>/ranking", get_ranking, name="ranking"),
    path("check_pronostics", check_pronostics, name="check_pronostics"),
    path("get_points", get_points, name="get_points"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("members.urls")),
]
