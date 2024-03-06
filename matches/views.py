from django.shortcuts import render
from django.views import generic

from players.models import Match, Result, PlayerStat


# Create your views here.
class MatchListView(generic.ListView):
    template_name = "matches/match_list.html"
    context_object_name = "matches"

    def get_queryset(self):
        queryset = Match.objects.all()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(MatchListView, self).get_context_data(**kwargs)
        queryset = Result.objects.all()
        context.update({
            "results": queryset
        })

        return context
    

class MatchDetailView(generic.DetailView):
    template_name = "matches/match_detail.html"
    context_object_name = "match"

    def get_queryset(self):
        queryset = Match.objects.all()

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        queryset = PlayerStat.objects.filter(
            match=self.get_object()
        )
        context.update({
            "hometeam_players": self.get_object().home_team.player_set.all(),
            "awayteam_players": self.get_object().away_team.player_set.all(),
            "players_stats": queryset
        })
        return context


