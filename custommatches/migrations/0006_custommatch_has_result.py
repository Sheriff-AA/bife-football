# Generated by Django 4.2.10 on 2024-07-29 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custommatches', '0005_alter_custommatch_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommatch',
            name='has_result',
            field=models.BooleanField(default=False),
        ),
    ]
