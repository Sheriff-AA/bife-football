from django.db import models
from django.contrib.auth.models import AbstractUser


PLAYER_POSITION = (
        ("CB", "Centre Back"),
        ("LCB", "Left Centre Back"),
        ("RCB", "Right Centre Back"),
        ("RB", "Right Back"),
        ("LB", "Left Back"),
        ("CM", "Center Midfield"),
        ("CAM", "Center Attacking Midfield"),
        ("LAM", "Left Attacking Midfield"),
        ("RAM", "Right Attacking Midfield"),
        ("LWB", "Left Wing Back"),
        ("RWB", "Right Wing Back"),
        ("ST", "Striker"),
        ("LW", "Left Wing"),
        ("RW", "Right Wing"),
    )


class User(AbstractUser):
    pass


class Team(models.Model):
    team_name = models.CharField(max_length=80, unique=True)
    short_team_name = models.CharField(unique=True, max_length=3)
    organisation = models.OneToOneField(
        on_delete=models.CASCADE,
        to=User,
        primary_key=True,
        related_name='team',
    )

    def __str__(self):
        return self.user.username


class Player(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    shirt_number = models.IntegerField()
    age = models.IntegerField(default=0)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    matches = models.ManyToManyField("Match", through="PlayerStat")
    position = models.CharField(max_length=30, blank=True, choices=PLAYER_POSITION)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class PlayerStat(models.Model):
    player = models.ForeignKey("Player", related_name="stats", on_delete=models.CASCADE)
    match = models.ForeignKey("Match", on_delete=models.CASCADE)
    goals = models.IntegerField()
    assists = models.IntegerField()
    minutes_played = models.IntegerField()


class Venue(models.Model):
    name = models.CharField(max_length=120)


class Match(models.Model):
    home_team = models.ForeignKey("Team", related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey("Team", related_name='away_matches', on_delete=models.CASCADE)
    venue = models.ForeignKey("Venue", null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)


class Result(models.Model):
    match = models.OneToOneField("Match", on_delete=models.CASCADE)
    score_hometeam = models.IntegerField()
    score_awayteam = models.IntegerField()

    def __str__(self):
        return f"{self.score_hometeam} - {self.score_awayteam}"
    
