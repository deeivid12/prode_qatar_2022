from django.core.management.base import BaseCommand

from tournaments.models import Game


class Command(BaseCommand):
    help = "Desbloquea el resultado de un partido para permitir sync externo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--external-id",
            type=int,
            required=True,
            help="External ID del partido en football-data.org",
        )

    def handle(self, *args, **options):
        external_id = options["external_id"]
        game = Game.objects.filter(external_id=external_id).first()
        if not game:
            self.stderr.write(
                self.style.ERROR(
                    f"No se encontró Game con external_id={external_id} en DB."
                )
            )
            return

        game.result_locked = False
        game.result_locked_reason = ""
        game.save(update_fields=["result_locked", "result_locked_reason"])
        self.stdout.write(
            self.style.SUCCESS(f"Partido {external_id} desbloqueado.")
        )
