# Generated by Django 4.1.1 on 2022-11-02 21:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0012_alter_game_penalties_win_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pronostic",
            name="last_modified",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 11, 2, 18, 42, 25, 476127)
            ),
        ),
    ]
