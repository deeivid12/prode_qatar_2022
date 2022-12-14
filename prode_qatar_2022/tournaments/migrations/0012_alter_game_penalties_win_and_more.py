# Generated by Django 4.1.1 on 2022-11-02 21:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0011_game_date_time_pronostic_last_modified"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="penalties_win",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "------------"), (1, "Home Team"), (2, "Away Team")],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="pronostic",
            name="last_modified",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 11, 2, 18, 41, 41, 537159)
            ),
        ),
    ]
