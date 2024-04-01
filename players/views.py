from django.shortcuts import render, redirect, reverse
from django.views import generic
from django.db.models import Sum, Count, Q

from .models import Player, PlayerStat, Contract, MatchEvent
from .forms import PlayerModelForm, PlayerModelUpdateForm


class LandingPageView(generic.TemplateView):
    template_name = "landing_page.html"


class PlayerListView(generic.ListView):
    template_name = "players/player_list.html"
    context_object_name = "players"

    def get_queryset(self):
        queryset = Player.objects.all()

        return queryset


class PlayerMatchesListView(generic.DetailView):
    template_name = "players/players_matches.html"
    context_object_name = "player"

    def get_queryset(self):
        queryset = Player.objects.all()

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(PlayerMatchesListView, self).get_context_data(**kwargs)
        queryset = PlayerStat.objects.filter(
            player=self.get_object()
            )
        context.update({
            "stats": queryset
        })

        return context
    

class PlayerDetailView(generic.DetailView):
    template_name = "players/player_detail.html"
    context_object_name = "player"

    def get_queryset(self):
        return Player.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(PlayerDetailView, self).get_context_data(**kwargs)
        contract = Contract.objects.filter(player=self.get_object()).order_by('-contract_date').first()
        latest_events = MatchEvent.objects.filter(player_contract=contract).order_by('-timestamp')[:5]
        queryset = PlayerStat.objects.filter(
            player=self.get_object()
            )
        context.update({
            "stats": queryset.aggregate(
                goals = Sum('goals', default=0),
                assists = Sum('assists', default=0),
                minutes_played = Sum('minutes_played', default=0),
                games = Count("match")),
            "contract": contract,
            "latest_events": latest_events
        })

        return context
    

class PlayerCreateView(generic.CreateView):
    template_name = "players/player_create.html"
    form_class = PlayerModelForm

    def get_success_url(self):
        return reverse("players:player-list")
    
    def form_valid(self, form):
        player = form.save(commit=False)
        player.save()
        return super(PlayerCreateView, self).form_valid(form)
    

class PlayerUpdateView(generic.UpdateView):
    template_name = "players/player_update.html"
    form_class = PlayerModelUpdateForm
    context_object_name = "player"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of players for entire team       
        return Player.objects.all()
        # return Player.objects.filter(teams=user)
    
    def get_success_url(self):
        return reverse("players:player-list")
    

class PlayerDeleteView(generic.DeleteView):
    template_name = "players/player_delete.html"
    context_object_name = "player"
    
    def get_queryset(self):
        user = self.request.user
        # initial queryset of players for entire team  
        return Player.objects.all()     
        # return Player.objects.filter(teams=user)

    def get_success_url(self):
        return reverse("players:player-list")