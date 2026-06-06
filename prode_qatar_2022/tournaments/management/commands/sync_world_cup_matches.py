import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from tournaments.integrations.football_data_client import FootballDataAPIError
from tournaments.models import Tournament
from tournaments.services.football_data_api import fetch_wc_matches
from tournaments.services.world_cup_matches import STAGE_CHOICES, sync_world_cup_matches

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Importa partidos del mundial desde football-data.org (API). "
        "Solo crea partidos con ambos equipos definidos (external_id no nulo)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--stage",
            type=str,
            default="ALL",
            choices=STAGE_CHOICES,
            help="Fase a importar: ALL, GROUP_STAGE, LAST_32, etc.",
        )
        parser.add_argument(
            "--tournament",
            type=str,
            default=None,
            help="Nombre del Tournament en DB (default: WORLD_CUP_TOURNAMENT_NAME)",
        )

    def handle(self, *args, **options):
        tournament_name = options["tournament"] or settings.WORLD_CUP_TOURNAMENT_NAME
        tournament = Tournament.objects.filter(name=tournament_name).first()
        if not tournament:
            logger.error('sync_world_cup_matches: tournament "%s" no encontrado', tournament_name)
            self.stderr.write(
                self.style.ERROR(f'Tournament "{tournament_name}" no encontrado en DB.')
            )
            return

        try:
            payload = fetch_wc_matches()
        except FootballDataAPIError as exc:
            logger.error("sync_world_cup_matches: error de API: %s", exc)
            self.stderr.write(self.style.ERROR(str(exc)))
            return
        except ValueError as exc:
            logger.error("sync_world_cup_matches: respuesta inválida: %s", exc)
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        try:
            result = sync_world_cup_matches(
                payload, tournament, stage=options["stage"]
            )
        except ValueError as exc:
            logger.error("sync_world_cup_matches: %s", exc)
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        created = len(result["created"])
        updated = len(result["updated"])
        skipped_tbd = len(result["skipped_undefined_teams"])
        skipped_team = len(result["skipped_missing_team"])
        logger.info(
            "sync_world_cup_matches stage=%s processed=%s created=%s updated=%s "
            "skipped_tbd=%s skipped_team=%s",
            result["stage"],
            result["processed"],
            created,
            updated,
            skipped_tbd,
            skipped_team,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'[{result["stage"]}] Procesados {result["processed"]} partidos de la API — '
                f"{created} creados, {updated} actualizados."
            )
        )
        if skipped_tbd:
            self.stdout.write(
                f"  Omitidos (equipos TBD): {skipped_tbd} — ids: "
                f"{result['skipped_undefined_teams'][:10]}"
                f"{'...' if skipped_tbd > 10 else ''}"
            )
        if skipped_team:
            self.stdout.write(
                self.style.WARNING(
                    f"  Omitidos (equipo no en DB): {skipped_team} — "
                    f"ejecutá sync_world_cup_teams primero."
                )
            )
        if result["skipped_unknown_stage"]:
            self.stdout.write(
                self.style.WARNING(
                    f"  Omitidos (stage desconocido): {result['skipped_unknown_stage']}"
                )
            )
