# Generated by Django 4.1.1 on 2022-11-03 18:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0014_alter_pronostic_last_modified_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pronostic",
            name="last_modified",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 11, 3, 15, 9, 1, 3929)
            ),
        ),
    ]
