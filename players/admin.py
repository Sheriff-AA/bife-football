from django.contrib import admin
from .models import (User, Team, Player, Match, PlayerStat, Contract, Venue, Result, Coach, MatchEvent, CustomMatch)

# Register your models here.
admin.site.register(User)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(CustomMatch)
admin.site.register(PlayerStat)
admin.site.register(Contract)
admin.site.register(Venue)
admin.site.register(Result)
admin.site.register(Coach)
admin.site.register(MatchEvent)
