from django.conf import settings
from django.core.management.base import BaseCommand
from pydantic import ValidationError

from tournaments.models import Tournament
from tournaments.services.world_cup_matches import (
    STAGE_CHOICES,
    load_world_cup_matches_file,
    sync_world_cup_matches,
)


class Command(BaseCommand):
    help = (
        "Importa partidos del mundial desde el JSON (football-data.org). "
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
            self.stderr.write(
                self.style.ERROR(f'Tournament "{tournament_name}" no encontrado en DB.')
            )
            return

        json_path = settings.WORLD_CUP_MATCHES_JSON
        try:
            payload = load_world_cup_matches_file(json_path)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {json_path}"))
            return
        except ValidationError as exc:
            self.stderr.write(self.style.ERROR(f"JSON inválido: {exc}"))
            return

        try:
            result = sync_world_cup_matches(
                payload, tournament, stage=options["stage"]
            )
        except ValueError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        created = len(result["created"])
        updated = len(result["updated"])
        skipped_tbd = len(result["skipped_undefined_teams"])
        skipped_team = len(result["skipped_missing_team"])

        self.stdout.write(
            self.style.SUCCESS(
                f'[{result["stage"]}] Procesados {result["processed"]} partidos del JSON — '
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
