# Generated by Django 4.1.1 on 2022-09-23 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0007_rename_tournamentroom_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='name',
            field=models.CharField(default='Mundialito', max_length=100),
            preserve_default=False,
        ),
    ]
