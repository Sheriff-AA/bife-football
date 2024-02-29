from django.shortcuts import render, redirect
from django.views import generic

from .models import Player


# Create your views here.
class PlayerListView(generic.ListView):
    template_name = "players/player_list.html"
    context_object_name = "players"

    def get_queryset(self):
        queryset = Player.objects.all()

        return queryset
    

class PlayerDetailView(generic.DetailView):
    template_name = "players/player_detail.html"
    context_object_name = "player"

    def get_queryset(self):
        queryset = Player.objects.all()

        return queryset