from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.generators import unique_slugify
import datetime


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
        return self.team_name
    

class Coach(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Player(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    shirt_number = models.IntegerField()
    slug = models.SlugField(null=True, blank=True, unique=True)
    age = models.IntegerField(default=0)
    teams = models.ManyToManyField("Team", through="Contract")
    matches = models.ManyToManyField("Match", through="PlayerStat")
    position = models.CharField(max_length=30, blank=True, choices=PLAYER_POSITION)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        new_slug = f"{self.first_name} {self.last_name}"
        unique_slugify(self, new_slug)
        super().save(*args, **kwargs)
    

class PlayerStat(models.Model):
    player = models.ForeignKey("Player", related_name="stats", on_delete=models.CASCADE)
    match = models.ForeignKey("Match", on_delete=models.CASCADE)
    goals = models.IntegerField()
    assists = models.IntegerField()
    minutes_played = models.IntegerField()


class Venue(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name}"


class Match(models.Model):
    home_team = models.ForeignKey("Team", related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey("Team", related_name='away_matches', on_delete=models.CASCADE)
    venue = models.ForeignKey("Venue", null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    

    def save(self, *args, **kwargs):
        new_slug = f"{self.home_team} vs {self.away_team}"
        unique_slugify(self,new_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.home_team} VS {self.away_team}"


class Result(models.Model):
    match = models.OneToOneField("Match", on_delete=models.CASCADE)
    score_hometeam = models.IntegerField()
    score_awayteam = models.IntegerField()

    def __str__(self):
        return f"{self.match} --> {self.score_hometeam} - {self.score_awayteam}"
    

class Contract(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    contract_date = models.DateField(default=datetime.date.today)
