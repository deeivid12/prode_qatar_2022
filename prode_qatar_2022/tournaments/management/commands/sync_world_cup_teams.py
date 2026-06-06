import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from tournaments.integrations.football_data_client import FootballDataAPIError
from tournaments.services.football_data_api import fetch_wc_teams
from tournaments.services.world_cup_teams import sync_teams_from_world_cup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Importa equipos del mundial desde football-data.org (API) a la base de datos."

    def handle(self, *args, **options):
        try:
            payload = fetch_wc_teams()
        except FootballDataAPIError as exc:
            logger.error("sync_world_cup_teams: error de API: %s", exc)
            self.stderr.write(self.style.ERROR(str(exc)))
            return
        except ValueError as exc:
            logger.error("sync_world_cup_teams: respuesta inválida: %s", exc)
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        result = sync_teams_from_world_cup(payload)
        created = len(result["created"])
        updated = len(result["updated"])
        logger.info(
            "sync_world_cup_teams: count=%s created=%s updated=%s",
            result["count"],
            created,
            updated,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Listo: {result['count']} equipos — {created} creados, {updated} actualizados."
            )
        )
