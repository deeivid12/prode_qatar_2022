from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0024_team_external_id_game_external_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="result_locked",
            field=models.BooleanField(
                default=False,
                help_text="Si es True, el sync externo no pisa el resultado cargado en DB.",
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="result_locked_reason",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Motivo del bloqueo manual del resultado.",
                max_length=255,
            ),
        ),
    ]
