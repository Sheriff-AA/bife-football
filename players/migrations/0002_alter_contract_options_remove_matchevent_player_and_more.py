# Generated by Django 4.2.10 on 2024-03-31 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contract',
            options={'ordering': ['-contract_date']},
        ),
        migrations.RemoveField(
            model_name='matchevent',
            name='player',
        ),
        migrations.AddField(
            model_name='matchevent',
            name='player_contract',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='players.contract'),
        ),
        migrations.AlterField(
            model_name='matchevent',
            name='related_player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_events', to='players.contract'),
        ),
    ]