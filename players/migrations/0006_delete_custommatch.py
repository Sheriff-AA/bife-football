# Generated by Django 4.2.10 on 2024-06-22 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0005_alter_custommatch_options_alter_match_options_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomMatch',
        ),
    ]
