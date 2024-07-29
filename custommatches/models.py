from django.db import models
from utils.generators import unique_slugify

from players.models import Player, MINUTES_CHOICES, Contract, Team, Venue, EVENT_CHOICES

# Create your models here.
class CustomMatch(models.Model):
    versus_team = models.CharField(max_length=40)
    user_team = models.ForeignKey(Team, related_name='custom_matches', on_delete=models.CASCADE)
    venue = models.CharField(max_length=20, null=False, blank=False)
    match_date = models.DateTimeField()
    slug = models.SlugField(null=True, blank=True, unique=True)
    is_fixture = models.BooleanField(default=True)
    has_result = models.BooleanField(default=False)
    is_home = models.BooleanField(default=False)

    class Meta:
        unique_together = ['versus_team','user_team', 'match_date']
        ordering = ['match_date']   

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
    

class CustomMatchPlayerStat(models.Model):
    player = models.ForeignKey(Player, related_name="custom_stats", on_delete=models.CASCADE)
    player_contract = models.ForeignKey(Contract, related_name="custom_stats", on_delete=models.CASCADE)
    custom_match = models.ForeignKey(CustomMatch, on_delete=models.CASCADE)
    goals = models.IntegerField()
    assists = models.IntegerField()
    minutes_played = models.IntegerField(choices=MINUTES_CHOICES)
    rating = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ['player_contract', 'custom_match']

    def __str__(self):
        return f"{self.player} in {self.custom_match}"
    

class CustomMatchEvent(models.Model):
    custom_match = models.ForeignKey(CustomMatch, on_delete=models.CASCADE, related_name='match_events')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    minute = models.PositiveSmallIntegerField(choices=MINUTES_CHOICES)
    player_contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True)
    related_player = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_related_events')
    is_own_goal = models.BooleanField(default=False)
    is_penalty = models.BooleanField(default=False)
    is_second_yellow_card = models.BooleanField(default=False)
    is_direct_red_card = models.BooleanField(default=False)

    class Meta:
        ordering = ['minute']

    def __str__(self):
        return f"{self.event_type} - Match: {self.custom_match}"
    
    def save(self, *args, **kwargs):
        # Check for and delete previous duplicates
        CustomMatchEvent.objects.filter(custom_match=self.custom_match, minute=self.minute, player_contract=self.player_contract, event_type=self.event_type).delete()
        # Save the new instance
        super().save(*args, **kwargs)
    

class CustomMatchResult(models.Model):
    custom_match = models.OneToOneField(CustomMatch, on_delete=models.CASCADE)
    score_userteam = models.IntegerField()
    score_versusteam = models.IntegerField(verbose_name='Opposition Score?')

    def __str__(self):
        if self.custom_match.is_home:
            return f"{self.custom_match}: {self.score_userteam} - {self.score_versusteam}"
        return f"{self.custom_match}: {self.score_versusteam} - {self.score_userteam}"
