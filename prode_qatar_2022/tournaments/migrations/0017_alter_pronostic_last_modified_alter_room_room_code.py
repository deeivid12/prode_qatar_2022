# Generated by Django 4.1.1 on 2022-11-03 20:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0016_room_room_code_alter_pronostic_last_modified"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pronostic",
            name="last_modified",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 11, 3, 17, 26, 25, 420259)
            ),
        ),
        migrations.AlterField(
            model_name="room",
            name="room_code",
            field=models.CharField(default="UJUWIZNH", max_length=8, unique=True),
        ),
    ]
