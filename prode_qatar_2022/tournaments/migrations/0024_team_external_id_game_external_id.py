from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0023_remove_pronostic_room"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="external_id",
            field=models.BigIntegerField(
                blank=True,
                db_index=True,
                help_text="ID del equipo en football-data.org",
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="external_id",
            field=models.BigIntegerField(
                blank=True,
                db_index=True,
                help_text="ID del partido en football-data.org",
                null=True,
                unique=True,
            ),
        ),
    ]
