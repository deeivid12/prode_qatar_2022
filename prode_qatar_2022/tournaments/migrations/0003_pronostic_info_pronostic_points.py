# Generated by Django 4.1.1 on 2022-09-20 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0002_pronostic_checked_alter_tournament_qty_teams'),
    ]

    operations = [
        migrations.AddField(
            model_name='pronostic',
            name='info',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='pronostic',
            name='points',
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
    ]
