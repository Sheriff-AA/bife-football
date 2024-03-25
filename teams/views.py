from django.shortcuts import render, reverse
from django.views import generic

from .forms import TeamModelForm
from players.models import Team


class TeamListView(generic.ListView):
    template_name = "teams/team_list.html"
    context_object_name = "teams"

    def get_queryset(self):
        queryset = Team.objects.all()
        return queryset


class TeamCreateView(generic.CreateView):
    template_name = "teams/team_create.html"
    form_class = TeamModelForm

    def get_success_url(self):
        return reverse("team:team-list")
    
    def form_valid(self, form):
        return super(TeamCreateView, self).form_valid(form)
