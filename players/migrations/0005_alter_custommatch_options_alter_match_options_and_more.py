# Generated by Django 4.2.10 on 2024-06-14 22:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_alter_custommatch_options_alter_match_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custommatch',
            options={'ordering': ['match_date']},
        ),
        migrations.AlterModelOptions(
            name='match',
            options={'ordering': ['match_date']},
        ),
        migrations.AlterModelOptions(
            name='matchevent',
            options={'ordering': ['minute']},
        ),
    ]