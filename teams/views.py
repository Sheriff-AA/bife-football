from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Subquery
from django.shortcuts import render, reverse, get_object_or_404
from django.conf import settings
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator

from players.mixins import CoachRequiredMixin
from .forms import TeamModelForm, TeamSelectForm
from players.models import Team, Contract, Match, Player, Result, Coach, PlayerStat
from custommatches.models import CustomMatch, CstmMatchResult

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
        contract = Contract.objects.filter(team=self.get_object(), is_valid=True).order_by('-contract_date')
        latest_contracts = contract.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        upcoming_matches = Match.objects.filter(Q(home_team=self.get_object()) | Q(away_team=self.get_object()))[:5]
        team_results = Result.objects.filter(Q(match__home_team=self.get_object()) | Q(match__away_team=self.get_object()))[:5]

        context.update({
            "contracts": latest_contracts,
            "upcoming_matches": upcoming_matches,
            "team_results": team_results,
            "selected_team": self.get_object()
        })

        return context


# if the request user 
class TeamDashboardView(generic.DetailView):
    Model = Player
    template_name = "teams/team_dashboard.html"
    context_object_name = "team"

    def get_object(self):
        # Get the player or coach  instance for the currently logged-in user
        if self.request.user.is_player:
            return get_object_or_404(Player, user=self.request.user)
        if self.request.user.is_coach:
            return get_object_or_404(Coach, user=self.request.user)
    

    def get_context_data(self, **kwargs):
        context = super(TeamDashboardView, self).get_context_data(**kwargs)
        user = self.get_object()

        # Get the selected team from the session, or default to the first team
        selected_team_id = self.request.session.get('selected_team_id')
        if self.request.user.is_player:
            selected_team = user.teams.filter(id=selected_team_id).first() if selected_team_id else user.teams.first()
        if self.request.user.is_coach:
            selected_team = user.team
        
        form = TeamSelectForm(user=user, initial={'team': selected_team})
        # team_stats = player.playerstat_set.filter(team=selected_team)
        
        context.update(self.get_dashboard_context(form, selected_team))
        return context
    
    def get_dashboard_context(self, form, selected_team):
        contract = Contract.objects.filter(team=selected_team, is_valid=True).order_by('-contract_date')
        latest_contracts = contract.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        upcoming_matches = Match.objects.filter(Q(home_team=selected_team) | Q(away_team=selected_team), is_fixture=True).order_by('match_date')[:5]
        team_results = Result.objects.filter(Q(match__home_team=selected_team) | Q(match__away_team=selected_team)).order_by('-match__match_date')[:5]

        player_stats = PlayerStat.objects.filter(match__in=Subquery(team_results.values("match")[:3]), player_contract__team=selected_team)

        # Group player stats by match
        matches_stats = {}
        for stat in player_stats:
            match_id = stat.match.id
            if match_id not in matches_stats:
                matches_stats[match_id] = {
                    'match': stat.match,
                    'player_stats': []
                }
            matches_stats[match_id]['player_stats'].append(stat)

        return {
            "contracts": latest_contracts,
            "upcoming_matches": upcoming_matches,
            "team_results": team_results,
            "selected_team": selected_team,
            "form": form,
            "matches_stats": matches_stats.values()
            # "team_stats": team_stats
        }
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        form = TeamSelectForm(request.POST, user=user)
        if form.is_valid():
            selected_team = form.cleaned_data['team']
            # Save the selected team in the session
            self.request.session['selected_team_id'] = selected_team.id
        else:
            if self.request.user.is_player:
                selected_team = user.teams.first()
            if self.request.user.is_coach:
                selected_team = user.team
        
        # team_stats = player.playerstat_set.filter(team=selected_team)

        if request.headers.get('HX-Request'):
            print(selected_team)
            return render(request, 'teams/partials/partial_team_dashboard.html', self.get_dashboard_context(form, selected_team))
        else:
            context = self.get_context_data()
            context.update(self.get_dashboard_context(form, selected_team))
            return self.render_to_response(context)
        

class TeamMatchesView(generic.DetailView):
    template_name = "teams/team_matches.html"
    context_object_name = "team"

    def get_queryset(self):
        return Team.objects.filter(slug=self.kwargs['slug'])
    
    
    def get_context_data(self, **kwargs):
        context = super(TeamMatchesView, self).get_context_data(**kwargs)
        list_type = self.request.GET.get("list_type", "results")
        team = self.get_object()

        if list_type == "fixtures":
            match_list = Match.objects.filter((Q(home_team=team) | Q(away_team=team)), is_fixture=True).order_by('match_date')
            custommatch_list = CustomMatch.objects.filter(Q(user_team=team), is_fixture=True).order_by('match_date')
        else:
            match_list = Result.objects.filter(Q(match__home_team=team) | Q(match__away_team=team)).order_by('-match__match_date')
            custommatch_list = CstmMatchResult.objects.filter(Q(custom_match__user_team=team)).order_by('-custom_match__match_date')

        context.update({"match_list": match_list,
                        "custommatch_list": custommatch_list,
                        "selected_team": team,
                        "list_type": list_type
                        })

        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if self.request.htmx:
            return render(request, "teams/partials/partial_team_matches_list.html", context)
        else:
            # Return the full page if not an HTMX request
            return super().get(request, *args, **kwargs)

    