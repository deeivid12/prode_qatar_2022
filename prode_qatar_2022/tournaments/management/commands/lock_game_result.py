from django.core.management.base import BaseCommand

from tournaments.models import Game


class Command(BaseCommand):
    help = "Bloquea el resultado de un partido para que no sea pisado por sync externo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--external-id",
            type=int,
            required=True,
            help="External ID del partido en football-data.org",
        )
        parser.add_argument(
            "--reason",
            type=str,
            default="",
            help="Motivo del bloqueo manual.",
        )

    def handle(self, *args, **options):
        external_id = options["external_id"]
        reason = options["reason"].strip()
        game = Game.objects.filter(external_id=external_id).first()
        if not game:
            self.stderr.write(
                self.style.ERROR(
                    f"No se encontró Game con external_id={external_id} en DB."
                )
            )
            return

        game.result_locked = True
        game.result_locked_reason = reason
        game.save(update_fields=["result_locked", "result_locked_reason"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Partido {external_id} bloqueado. "
                f"Motivo: {reason if reason else '(sin motivo)'}"
            )
        )
