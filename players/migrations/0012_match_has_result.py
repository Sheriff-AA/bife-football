# Generated by Django 4.2.10 on 2024-07-29 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0011_team_team_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='has_result',
            field=models.BooleanField(default=False),
        ),
    ]
