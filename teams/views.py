from django.shortcuts import render, reverse, get_object_or_404
from django.conf import settings
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator

from players.mixins import PlayerOrCoachAndLoginRequiredMixin
from .forms import TeamModelForm, TeamSelectForm
from players.models import Team, Contract, Match, Player, Result

GET_LATEST_CONTRACTS = settings.GET_LATEST_CONTRACTS


class TeamListView(generic.ListView):
    template_name = "teams/team_list.html"
    paginate_by = 10
    context_object_name = "teams"

    def get_queryset(self):
        return Team.objects.all().order_by('id')
    
    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
        qs = self.get_queryset()
        if search:
            qs = self.get_queryset().filter(Q(team_name__icontains=search) | Q(short_team_name__icontains=search))

        paginator = Paginator(qs, 15)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        if request.htmx:
            return render(request, 'teams/partials/partial_team_list.html', {'page_obj': page_obj})
        else:
            return render(request, 'teams/team_list.html', {'page_obj': page_obj})


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
            where=[GET_LATEST_CONTRACTS]
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


# if the request user 
class TeamDashboardView(generic.DetailView):
    Model = Player
    template_name = "teams/team_dashboard.html"
    context_object_name = "team"

    def get_object(self):
        # Get the Player instance for the currently logged-in user
        return get_object_or_404(Player, user=self.request.user)
    

    def get_context_data(self, **kwargs):
        context = super(TeamDashboardView, self).get_context_data(**kwargs)

        player = self.get_object()
        form = TeamSelectForm(player=player)
        selected_team = player.teams.first()
        # team_stats = player.playerstat_set.filter(team=selected_team)
        
        context.update(self.get_dashboard_context(form, selected_team))
        return context
    
    def get_dashboard_context(self, form, selected_team):
        contract = Contract.objects.filter(team=selected_team).order_by('-contract_date')
        latest_contracts = contract.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        upcoming_matches = Match.objects.filter(Q(home_team=selected_team) | Q(away_team=selected_team))[:10]
        team_results = Result.objects.filter(Q(match__home_team=selected_team) | Q(match__away_team=selected_team)
            )

        return {
            "contracts": latest_contracts,
            "upcoming_matches": upcoming_matches,
            "team_results": team_results,
            "selected_team": selected_team,
            "form": form,
            # "team_stats": team_stats
        }
    
    def post(self, request, *args, **kwargs):
        player = self.get_object()
        form = TeamSelectForm(request.POST, player=player)
        if form.is_valid():
            selected_team = form.cleaned_data['team']
        else:
            selected_team = player.teams.first()
        
        # team_stats = player.playerstat_set.filter(team=selected_team)

        if request.headers.get('HX-Request'):
            print(selected_team)
            return render(request, 'teams/partials/partial_team_dashboard.html', self.get_dashboard_context(form, selected_team))
        else:
            context = self.get_context_data()
            context.update(self.get_dashboard_context(form, selected_team))
            return self.render_to_response(context)