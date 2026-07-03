import pytest
from django.contrib.auth.models import User

from commons.tournaments import check_pronostics_results, check_pronostics_results_v2
from tournaments.models import Game, Pronostic, Team, Tournament


@pytest.fixture
def tournament_with_games(db):
    tournament = Tournament.objects.create(name="Test", qty_teams=4)
    home = Team.objects.create(name="Home", fifa_code="HOM")
    away = Team.objects.create(name="Away", fifa_code="AWY")
    played_game = Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time="2026-07-01T19:00:00Z",
        home_goals=2,
        away_goals=1,
        played=True,
    )
    future_game = Game.objects.create(
        home_team=home,
        away_team=away,
        tournament=tournament,
        date_time="2026-07-10T19:00:00Z",
        played=False,
    )
    return played_game, future_game


@pytest.mark.django_db
def test_v2_scores_played_game_and_skips_future(tournament_with_games):
    played_game, future_game = tournament_with_games
    exact = Pronostic.objects.create(
        game=played_game,
        user=User.objects.create_user(username="u1", password="pass"),
        home_goals=2,
        away_goals=1,
    )
    diff = Pronostic.objects.create(
        game=played_game,
        user=User.objects.create_user(username="u2", password="pass"),
        home_goals=3,
        away_goals=2,
    )
    future = Pronostic.objects.create(
        game=future_game,
        user=User.objects.create_user(username="u3", password="pass"),
        home_goals=1,
        away_goals=0,
    )

    check_pronostics_results_v2()

    exact.refresh_from_db()
    diff.refresh_from_db()
    future.refresh_from_db()

    assert exact.checked is True and exact.points == 5
    assert diff.checked is True and diff.points == 3
    assert future.checked is False and future.points is None


@pytest.mark.django_db
def test_v2_matches_v1_results(tournament_with_games):
    played_game, future_game = tournament_with_games

    def make_pronostics(suffix):
        users = []
        for i, (hg, ag) in enumerate([(2, 1), (3, 2), (0, 0)]):
            users.append(
                User.objects.create_user(username=f"p{i}_{suffix}", password="pass")
            )
            Pronostic.objects.create(
                game=played_game,
                user=users[-1],
                home_goals=hg,
                away_goals=ag,
            )
        Pronostic.objects.create(
            game=future_game,
            user=User.objects.create_user(username=f"future_{suffix}", password="pass"),
            home_goals=1,
            away_goals=0,
        )

    make_pronostics("v2")
    check_pronostics_results_v2()
    v2_results = list(
        Pronostic.objects.filter(game=played_game, user__username__endswith="_v2")
        .order_by("user__username")
        .values_list("checked", "points")
    )

    make_pronostics("v1")
    check_pronostics_results()
    v1_results = list(
        Pronostic.objects.filter(game=played_game, user__username__endswith="_v1")
        .order_by("user__username")
        .values_list("checked", "points")
    )

    assert v2_results == v1_results
