# Generated by Django 4.2.10 on 2024-04-01 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0003_alter_playerstat_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coach',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coach', to='players.team'),
        ),
    ]