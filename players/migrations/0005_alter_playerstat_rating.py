# Generated by Django 4.2.10 on 2024-03-13 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_playerstat_rating_playerstat_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerstat',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]