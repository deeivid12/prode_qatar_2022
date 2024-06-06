# Generated by Django 4.1.1 on 2022-11-09 17:53

import commons.utils
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0017_alter_pronostic_last_modified_alter_room_room_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="fifa_code",
            field=models.CharField(blank=True, max_length=3),
        ),
        migrations.AlterField(
            model_name="pronostic",
            name="last_modified",
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name="room",
            name="room_code",
            field=models.CharField(
                default=commons.utils.generate_room_code, max_length=8, unique=True
            ),
        ),
    ]
