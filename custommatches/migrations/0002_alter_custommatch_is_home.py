# Generated by Django 4.2.10 on 2024-06-22 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custommatches', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custommatch',
            name='is_home',
            field=models.BooleanField(default=False),
        ),
    ]
