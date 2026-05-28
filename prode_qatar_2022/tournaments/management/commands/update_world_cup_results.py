from django.conf import settings
from django.core.management.base import BaseCommand
from pydantic import ValidationError

from tournaments.services.world_cup_matches import (
    load_world_cup_matches_file,
    update_world_cup_results,
)


class Command(BaseCommand):
    help = (
        "Actualiza resultados de partidos del mundial desde el JSON "
        "(goles de tiempo regular, played y ganador por penales si aplica). "
        "Recalcula puntos de pronósticos pendientes."
    )

    def handle(self, *args, **options):
        json_path = settings.WORLD_CUP_MATCHES_JSON
        try:
            payload = load_world_cup_matches_file(json_path)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {json_path}"))
            return
        except ValidationError as exc:
            self.stderr.write(self.style.ERROR(f"JSON inválido: {exc}"))
            return

        result = update_world_cup_results(payload)

        self.stdout.write(
            self.style.SUCCESS(
                f"Actualizados {result['updated_count']} partido(s). "
                f"Pronósticos revisados."
            )
        )
        if result["skipped_not_in_db"]:
            self.stdout.write(
                f"  No estaban en DB: {len(result['skipped_not_in_db'])} partido(s)"
            )
        if result["skipped_no_score"]:
            self.stdout.write(
                f"  Finalizados sin marcador en JSON: {result['skipped_no_score']}"
            )
