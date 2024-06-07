from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.generators import unique_slugify
import datetime


PLAYER_POSITION = (
    ("GK", "Goalkeeper"),
    ("CB", "Centre Back"),
    ("LCB", "Left Centre Back"),
    ("RCB", "Right Centre Back"),
    ("RB", "Right Back"),
    ("LB", "Left Back"),
    ("CM", "Center Midfield"),
    ("CDM", "Center Defensive Midfield"),
    ("CAM", "Center Attacking Midfield"),
    ("LAM", "Left Attacking Midfield"),
    ("RAM", "Right Attacking Midfield"),
    ("LWB", "Left Wing Back"),
    ("RWB", "Right Wing Back"),
    ("ST", "Striker"),
    ("CF", "Center Forward"),
    ("LW", "Left Wing"),
    ("RW", "Right Wing"),
    )

MINUTES_CHOICES = [(i, f"{i}'") for i in range(1, 121)]


class User(AbstractUser):
    is_coach = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_player = models.BooleanField(default=False)


class Team(models.Model):
    team_name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    short_team_name = models.CharField(unique=True, max_length=3)
    organisation = models.ForeignKey("User",
        on_delete=models.CASCADE,
        related_name='team'
    ) # remember to filter for one organisation, a user can have multiple teams

    def __str__(self):
        return self.team_name
    
    def save(self, *args, **kwargs):
        new_slug = f"{self.team_name}"
        unique_slugify(self, new_slug)
        super().save(*args, **kwargs)
    

class Coach(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name='coach')
    user = models.OneToOneField("User", on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Player(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    shirt_number = models.IntegerField()
    slug = models.SlugField(null=True, blank=True, unique=True)
    age = models.IntegerField(default=0)
    user = models.OneToOneField("User", on_delete=models.CASCADE)
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
    player_contract = models.ForeignKey("Contract", related_name="stats", on_delete=models.CASCADE)
    match = models.ForeignKey("Match", on_delete=models.CASCADE)
    goals = models.IntegerField()
    assists = models.IntegerField()
    minutes_played = models.IntegerField(choices=MINUTES_CHOICES)
    rating = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ['player_contract', 'match']

    def __str__(self):
        return f"{self.player} in {self.match}"
    

class Venue(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.name}"


class Match(models.Model):
    home_team = models.ForeignKey("Team", related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey("Team", related_name='away_matches', on_delete=models.CASCADE)
    venue = models.ForeignKey("Venue", null=True, blank=True, on_delete=models.SET_NULL)
    match_date = models.DateTimeField()
    slug = models.SlugField(null=True, blank=True, unique=True)
    is_fixture = models.BooleanField(default=True)

    class Meta:
        unique_together = ['home_team', 'away_team', 'match_date']    

    def save(self, *args, **kwargs):
        new_slug = f"{self.home_team} vs {self.away_team}"
        unique_slugify(self,new_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.home_team} ({self.home_team.short_team_name}) vs {self.away_team} ({self.away_team.short_team_name})"


class Result(models.Model):
    match = models.OneToOneField("Match", on_delete=models.CASCADE)
    score_hometeam = models.IntegerField()
    score_awayteam = models.IntegerField()

    def __str__(self):
        return f"{self.match}: {self.score_hometeam} - {self.score_awayteam}"
    

class Contract(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    contract_date = models.DateField(default=datetime.date.today)
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['player', 'team', 'contract_date']
        ordering = ['-contract_date']

    def __str__(self):
        return f"{self.player} for {self.team.short_team_name}"


class MatchEvent(models.Model):
    EVENT_CHOICES = (
        ('GOAL', 'Goal'),
        ('ASSIST', 'Assist'),
        ('YELLOW_CARD', 'Yellow Card'),
        ('RED_CARD', 'Red Card'),
        ('SUBSTITUTION', 'Substitution'),
        ('HALFTIME', 'Halftime'),
        ('FULLTIME', 'Fulltime'),
    )

    match = models.ForeignKey('Match', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    minute = models.PositiveSmallIntegerField(choices=MINUTES_CHOICES)
    player_contract = models.ForeignKey('Contract', on_delete=models.CASCADE, null=True, blank=True)
    related_player = models.ForeignKey('Contract', on_delete=models.CASCADE, null=True, blank=True, related_name='related_events')
    is_own_goal = models.BooleanField(default=False)
    is_penalty = models.BooleanField(default=False)
    is_second_yellow_card = models.BooleanField(default=False)
    is_direct_red_card = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event_type} - Match: {self.match}"
    

class CustomMatch(models.Model):
    versus_team = models.CharField(max_length=40)
    user_team = models.ForeignKey("Team", related_name='custom_matches', on_delete=models.CASCADE)
    venue = models.ForeignKey("Venue", null=True, blank=True, on_delete=models.SET_NULL)
    match_date = models.DateTimeField()
    slug = models.SlugField(null=True, blank=True, unique=True)
    is_fixture = models.BooleanField(default=True)
    is_home = models.BooleanField(default=True)

    class Meta:
        unique_together = ['versus_team','user_team', 'match_date']    

    def save(self, *args, **kwargs):
        if self.is_home:
            new_slug =  f"{self.user_team} vs {self.versus_team}"
        else:
            new_slug = f"{self.versus_team} vs {self.user_team}"
        unique_slugify(self,new_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_home:
            return f"{self.user_team} vs {self.versus_team}" 
        return f"{self.versus_team} vs {self.user_team}"