# Generated by Django 4.2.10 on 2024-06-22 00:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('players', '0006_delete_custommatch'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('versus_team', models.CharField(max_length=40)),
                ('match_date', models.DateTimeField()),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('is_fixture', models.BooleanField(default=True)),
                ('is_home', models.BooleanField(default=True)),
                ('user_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_matches', to='players.team')),
                ('venue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='players.venue')),
            ],
            options={
                'ordering': ['match_date'],
                'unique_together': {('versus_team', 'user_team', 'match_date')},
            },
        ),
        migrations.CreateModel(
            name='CstmMatchResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_userteam', models.IntegerField()),
                ('score_versusteam', models.IntegerField()),
                ('custom_match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='custommatches.custommatch')),
            ],
        ),
        migrations.CreateModel(
            name='CstmMatchEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('GOAL', 'Goal'), ('ASSIST', 'Assist'), ('YELLOW_CARD', 'Yellow Card'), ('RED_CARD', 'Red Card'), ('SUBSTITUTION', 'Substitution'), ('HALFTIME', 'Halftime'), ('FULLTIME', 'Fulltime')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('minute', models.PositiveSmallIntegerField(choices=[(1, "1'"), (2, "2'"), (3, "3'"), (4, "4'"), (5, "5'"), (6, "6'"), (7, "7'"), (8, "8'"), (9, "9'"), (10, "10'"), (11, "11'"), (12, "12'"), (13, "13'"), (14, "14'"), (15, "15'"), (16, "16'"), (17, "17'"), (18, "18'"), (19, "19'"), (20, "20'"), (21, "21'"), (22, "22'"), (23, "23'"), (24, "24'"), (25, "25'"), (26, "26'"), (27, "27'"), (28, "28'"), (29, "29'"), (30, "30'"), (31, "31'"), (32, "32'"), (33, "33'"), (34, "34'"), (35, "35'"), (36, "36'"), (37, "37'"), (38, "38'"), (39, "39'"), (40, "40'"), (41, "41'"), (42, "42'"), (43, "43'"), (44, "44'"), (45, "45'"), (46, "46'"), (47, "47'"), (48, "48'"), (49, "49'"), (50, "50'"), (51, "51'"), (52, "52'"), (53, "53'"), (54, "54'"), (55, "55'"), (56, "56'"), (57, "57'"), (58, "58'"), (59, "59'"), (60, "60'"), (61, "61'"), (62, "62'"), (63, "63'"), (64, "64'"), (65, "65'"), (66, "66'"), (67, "67'"), (68, "68'"), (69, "69'"), (70, "70'"), (71, "71'"), (72, "72'"), (73, "73'"), (74, "74'"), (75, "75'"), (76, "76'"), (77, "77'"), (78, "78'"), (79, "79'"), (80, "80'"), (81, "81'"), (82, "82'"), (83, "83'"), (84, "84'"), (85, "85'"), (86, "86'"), (87, "87'"), (88, "88'"), (89, "89'"), (90, "90'"), (91, "91'"), (92, "92'"), (93, "93'"), (94, "94'"), (95, "95'"), (96, "96'"), (97, "97'"), (98, "98'"), (99, "99'"), (100, "100'"), (101, "101'"), (102, "102'"), (103, "103'"), (104, "104'"), (105, "105'"), (106, "106'"), (107, "107'"), (108, "108'"), (109, "109'"), (110, "110'"), (111, "111'"), (112, "112'"), (113, "113'"), (114, "114'"), (115, "115'"), (116, "116'"), (117, "117'"), (118, "118'"), (119, "119'"), (120, "120'")])),
                ('is_own_goal', models.BooleanField(default=False)),
                ('is_penalty', models.BooleanField(default=False)),
                ('is_second_yellow_card', models.BooleanField(default=False)),
                ('is_direct_red_card', models.BooleanField(default=False)),
                ('custom_match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custommatches.custommatch')),
                ('player_contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='players.contract')),
                ('related_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_related_events', to='players.contract')),
            ],
            options={
                'ordering': ['minute'],
            },
        ),
        migrations.CreateModel(
            name='CstmMatchPlayerStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('minutes_played', models.IntegerField(choices=[(1, "1'"), (2, "2'"), (3, "3'"), (4, "4'"), (5, "5'"), (6, "6'"), (7, "7'"), (8, "8'"), (9, "9'"), (10, "10'"), (11, "11'"), (12, "12'"), (13, "13'"), (14, "14'"), (15, "15'"), (16, "16'"), (17, "17'"), (18, "18'"), (19, "19'"), (20, "20'"), (21, "21'"), (22, "22'"), (23, "23'"), (24, "24'"), (25, "25'"), (26, "26'"), (27, "27'"), (28, "28'"), (29, "29'"), (30, "30'"), (31, "31'"), (32, "32'"), (33, "33'"), (34, "34'"), (35, "35'"), (36, "36'"), (37, "37'"), (38, "38'"), (39, "39'"), (40, "40'"), (41, "41'"), (42, "42'"), (43, "43'"), (44, "44'"), (45, "45'"), (46, "46'"), (47, "47'"), (48, "48'"), (49, "49'"), (50, "50'"), (51, "51'"), (52, "52'"), (53, "53'"), (54, "54'"), (55, "55'"), (56, "56'"), (57, "57'"), (58, "58'"), (59, "59'"), (60, "60'"), (61, "61'"), (62, "62'"), (63, "63'"), (64, "64'"), (65, "65'"), (66, "66'"), (67, "67'"), (68, "68'"), (69, "69'"), (70, "70'"), (71, "71'"), (72, "72'"), (73, "73'"), (74, "74'"), (75, "75'"), (76, "76'"), (77, "77'"), (78, "78'"), (79, "79'"), (80, "80'"), (81, "81'"), (82, "82'"), (83, "83'"), (84, "84'"), (85, "85'"), (86, "86'"), (87, "87'"), (88, "88'"), (89, "89'"), (90, "90'"), (91, "91'"), (92, "92'"), (93, "93'"), (94, "94'"), (95, "95'"), (96, "96'"), (97, "97'"), (98, "98'"), (99, "99'"), (100, "100'"), (101, "101'"), (102, "102'"), (103, "103'"), (104, "104'"), (105, "105'"), (106, "106'"), (107, "107'"), (108, "108'"), (109, "109'"), (110, "110'"), (111, "111'"), (112, "112'"), (113, "113'"), (114, "114'"), (115, "115'"), (116, "116'"), (117, "117'"), (118, "118'"), (119, "119'"), (120, "120'")])),
                ('rating', models.DecimalField(decimal_places=2, max_digits=5)),
                ('custom_match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='custommatches.custommatch')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_stats', to='players.player')),
                ('player_contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_stats', to='players.contract')),
            ],
            options={
                'unique_together': {('player_contract', 'custom_match')},
            },
        ),
    ]