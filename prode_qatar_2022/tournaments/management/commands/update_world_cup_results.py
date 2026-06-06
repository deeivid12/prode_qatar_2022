import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from tournaments.integrations.football_data_client import FootballDataAPIError
from tournaments.services.football_data_api import load_wc_matches_payload
from tournaments.services.world_cup_matches import update_world_cup_results

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Actualiza resultados de partidos del mundial y recalcula puntos de pronósticos. "
        "Por defecto usa football-data.org (API). Con --from-json usa un archivo local."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-json",
            nargs="?",
            const="",
            default=None,
            metavar="PATH",
            help=(
                "Usar JSON local en lugar de la API. "
                "Si no se indica PATH, usa WORLD_CUP_MATCHES_JSON."
            ),
        )

    def handle(self, *args, **options):
        json_option = options["from_json"]
        if json_option is not None:
            json_path = json_option or settings.WORLD_CUP_MATCHES_JSON
            try:
                payload = load_wc_matches_payload(json_path=json_path)
            except FileNotFoundError as exc:
                logger.error("update_world_cup_results: %s", exc)
                self.stderr.write(self.style.ERROR(str(exc)))
                return
            except ValueError as exc:
                logger.error("update_world_cup_results: JSON inválido: %s", exc)
                self.stderr.write(self.style.ERROR(str(exc)))
                return
            source_label = f"JSON ({json_path})"
        else:
            try:
                payload = load_wc_matches_payload(status="FINISHED")
            except FootballDataAPIError as exc:
                logger.error("update_world_cup_results: error de API: %s", exc)
                self.stderr.write(self.style.ERROR(str(exc)))
                return
            except ValueError as exc:
                logger.error("update_world_cup_results: respuesta inválida: %s", exc)
                self.stderr.write(self.style.ERROR(str(exc)))
                return
            source_label = "API (FINISHED)"

        result = update_world_cup_results(payload)

        logger.info(
            "update_world_cup_results source=%s updated=%s skipped_not_in_db=%s "
            "skipped_no_score=%s skipped_locked=%s",
            source_label,
            result["updated_count"],
            len(result["skipped_not_in_db"]),
            len(result["skipped_no_score"]),
            len(result["skipped_locked"]),
        )

        self._write_result(result, source_label)

    def _write_result(self, result, source_label):
        self.stdout.write(
            self.style.SUCCESS(
                f"[{source_label}] Actualizados {result['updated_count']} partido(s). "
                f"Pronósticos revisados."
            )
        )
        if result["skipped_not_in_db"]:
            self.stdout.write(
                f"  No estaban en DB: {len(result['skipped_not_in_db'])} partido(s)"
            )
        if result["skipped_no_score"]:
            self.stdout.write(
                f"  Finalizados sin marcador: {len(result['skipped_no_score'])} partido(s)"
            )
        if result["skipped_locked"]:
            self.stdout.write(
                self.style.WARNING(
                    "  Omitidos por bloqueo manual en DB: "
                    f"{len(result['skipped_locked'])} partido(s)"
                )
            )
