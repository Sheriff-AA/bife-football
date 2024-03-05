from django.shortcuts import render
from django.views import generic

from players.models import Match


# Create your views here.
class MatchList(generic.ListView):
    template_name = "matches/match_list.html"
    context_object_name = "matches"

    def get_queryset(self):
        queryset = Match.objects.all()

        return queryset
