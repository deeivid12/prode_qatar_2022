import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from tournaments.integrations.football_data_client import FootballDataAPIError
from tournaments.models import Tournament
from tournaments.services.football_data_api import load_wc_matches_payload
from tournaments.services.match_window import get_active_games, has_active_matches
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
        parser.add_argument(
            "--only-if-active",
            action="store_true",
            help=(
                "Solo ejecuta si hay partidos en ventana activa "
                "(MINUTES_BEFORE_GAME / MATCH_WINDOW_AFTER_KICKOFF)."
            ),
        )
        parser.add_argument(
            "--tournament",
            type=str,
            default=None,
            help="Nombre del Tournament en DB (default: WORLD_CUP_TOURNAMENT_NAME)",
        )

    def handle(self, *args, **options):
        if options["only_if_active"]:
            try:
                tournament_id = self._resolve_tournament_id(options["tournament"])
            except CommandError as exc:
                logger.error("update_world_cup_results: %s", exc)
                self.stderr.write(self.style.ERROR(str(exc)))
                return
            if not has_active_matches(tournament_id):
                logger.info(
                    "update_world_cup_results: sin partidos activos, ejecución omitida"
                )
                self.stdout.write("Sin partidos activos, ejecución omitida.")
                return

            active_games = get_active_games(tournament_id)
            logger.info(
                "update_world_cup_results: partidos activos=%s ids=%s",
                active_games.count(),
                list(active_games.values_list("id", flat=True)),
            )

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

    def _resolve_tournament_id(self, tournament_name):
        if tournament_name:
            tournament = Tournament.objects.filter(name=tournament_name).first()
            if not tournament:
                raise CommandError(f'Tournament "{tournament_name}" no encontrado.')
            return tournament.id

        tournament = Tournament.objects.filter(
            name=settings.WORLD_CUP_TOURNAMENT_NAME
        ).first()
        return tournament.id if tournament else None
