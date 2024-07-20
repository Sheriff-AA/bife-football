# Generated by Django 4.2.10 on 2024-07-14 23:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0007_alter_matchevent_match'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='user',
        ),
        migrations.AlterField(
            model_name='coach',
            name='team',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coach', to='players.team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='venue',
            field=models.CharField(max_length=20),
        ),
    ]