# Generated by Django 4.2.10 on 2024-05-15 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
    ]
