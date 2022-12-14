# Generated by Django 4.1.1 on 2022-09-20 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pronostic',
            name='checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='qty_teams',
            field=models.PositiveSmallIntegerField(default=20, verbose_name='Quantity Teams'),
        ),
    ]
