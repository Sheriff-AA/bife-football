from django.shortcuts import render, reverse
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator


from .forms import TeamModelForm
from players.models import Team, Contract, Match, Result


class TeamListView(generic.ListView):
    template_name = "teams/team_list.html"
    paginate_by = 10
    context_object_name = "teams"

    def get_queryset(self):
        queryset = Team.objects.all().order_by('id')
        return queryset


class TeamCreateView(generic.CreateView):
    template_name = "teams/team_create.html"
    form_class = TeamModelForm

    def get_success_url(self):
        return reverse("team:team-list")
    
    def form_valid(self, form):
        return super(TeamCreateView, self).form_valid(form)


class TeamDetailView(generic.DetailView):
    template_name = "teams/team_detail.html"
    context_object_name = "team"

    def get_queryset(self):
        return Team.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        contract = Contract.objects.filter(team=self.get_object()).order_by('-contract_date')
        latest_contracts = contract.extra(
            where=[
            '''id IN (SELECT id FROM (SELECT id, ROW_NUMBER() 
            OVER (PARTITION BY player_id ORDER BY contract_date DESC) AS rn 
            FROM players_contract) AS subquery 
            WHERE rn = 1)'''
            ]
        )
        upcoming_matches = Match.objects.filter(Q(home_team=self.get_object()) | Q(away_team=self.get_object()))[:10]
        team_results = Result.objects.filter(Q(match__home_team=self.get_object()) | Q(match__away_team=self.get_object())
            )
        context.update({
            "contracts": latest_contracts,
            "upcoming_matches": upcoming_matches,
            "team_results": team_results
        })

        return context
