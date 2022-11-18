# Generated by Django 4.1.1 on 2022-11-18 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0021_game_played"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="game_instance",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Groups"),
                    (1, "Round of 16"),
                    (2, "Quarter-Finals"),
                    (3, "Semi-Finals"),
                    (4, "Finals"),
                ],
                default=0,
            ),
        ),
    ]
