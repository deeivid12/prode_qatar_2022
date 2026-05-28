from django.conf import settings
from django.core.management.base import BaseCommand
from pydantic import ValidationError

from tournaments.services.world_cup_teams import (
    load_world_cup_teams_file,
    sync_teams_from_world_cup,
)


class Command(BaseCommand):
    help = "Importa equipos del mundial desde el JSON (football-data.org) a la base de datos."

    def handle(self, *args, **options):
        json_path = settings.WORLD_CUP_TEAMS_JSON
        try:
            payload = load_world_cup_teams_file(json_path)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {json_path}"))
            return
        except ValidationError as exc:
            self.stderr.write(self.style.ERROR(f"JSON inválido: {exc}"))
            return

        result = sync_teams_from_world_cup(payload)
        created = len(result["created"])
        updated = len(result["updated"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Listo: {result['count']} equipos — {created} creados, {updated} actualizados."
            )
        )
