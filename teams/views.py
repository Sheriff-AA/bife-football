import random
from typing import Any
# from django.db.models.query import QuerySet
from django.db.models import Subquery
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.conf import settings
from faker import Faker
from django.contrib import messages
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin

from players.mixins import AdminorCoachRequiredMixin, CoachRequiredMixin, AdminRequiredMixin
from .forms import TeamModelForm, TeamSelectForm, CoachModelForm
from players.models import Team, Contract, Match, Player, Result, Coach, PlayerStat, User
from admins.models import Admin
from custommatches.models import CustomMatch, CustomMatchResult, CustomMatchPlayerStat

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


class TeamCreateView(AdminRequiredMixin, generic.CreateView):
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
        upcoming_matches = Match.objects.filter(Q(home_team=self.get_object()) | Q(away_team=self.get_object()), is_fixture=True).order_by('-match_date')[:5]
        custom_matches = CustomMatch.objects.filter(Q(user_team=self.get_object()), is_fixture=True).order_by('-match_date')[:5]

        team_results = Result.objects.filter(Q(match__home_team=self.get_object()) | Q(match__away_team=self.get_object())).order_by('-match__match_date')[:5]
        custom_results = CustomMatchResult.objects.filter(Q(custom_match__user_team=self.get_object())).order_by('-custom_match__match_date')[:5]

        context.update({
            "contracts": latest_contracts,
            "upcoming_matches": upcoming_matches,
            "custom_matches": custom_matches,
            "custom_results": custom_results,
            "team_results": team_results,
            "selected_team": self.get_object()
        })

        return context


class TeamDashboardView(LoginRequiredMixin, AdminorCoachRequiredMixin, generic.DetailView):
    model = Player
    template_name = "teams/team_dashboard.html"
    context_object_name = "team"

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        self.ensure_default_team_in_session(user)
        selected_team_id = self.request.session.get('selected_team_id')

        if hasattr(user, 'player'):
            selected_team = self.get_valid_team(user.player.teams, selected_team_id)
        elif hasattr(user, 'coach'):
            selected_team = user.coach.team

        
        form = TeamSelectForm(user=user, initial={'team': selected_team})
        # team_stats = player.playerstat_set.filter(team=selected_team)
        
        context.update(self.get_dashboard_context(form, selected_team))
        return context
    
    def ensure_default_team_in_session(self, user):
        if 'selected_team_id' not in self.request.session:
            if hasattr(user, 'player'):
                first_team = user.player.teams.first()
            elif hasattr(user, 'coach'):
                first_team = user.coach.team
            self.request.session['selected_team_id'] = first_team.id
    
    def get_valid_team(self, teams, selected_team_id):
        # Ensure the selected team exists and belongs to the user
        if selected_team_id:
            selected_team = teams.filter(id=selected_team_id).first()
            if selected_team:
                return selected_team
        # Default to the first team if the selected team is invalid
        return teams.first()
    
    def group_stats(self, stats, queryset, is_custom):
        for stat in queryset:
            if is_custom:
                match_id = stat.custom_match.id
            else:
                match_id = stat.match.id
            if match_id not in stats:
                if is_custom:
                    match = stat.custom_match
                else:
                    match = stat.match
                stats[match_id] = {
                    'match': match,
                    'player_stats': []
                }
            stats[match_id]['player_stats'].append(stat)
        
        return stats
    
    def get_dashboard_context(self, form, selected_team):
        contract = Contract.objects.filter(team=selected_team, is_valid=True).order_by('-contract_date')
        latest_contracts = contract.extra(where=[GET_LATEST_CONTRACTS])
        upcoming_matches = Match.objects.filter(Q(home_team=selected_team) | Q(away_team=selected_team), is_fixture=True).order_by('match_date')[:5]
        team_results = Result.objects.filter(Q(match__home_team=selected_team) | Q(match__away_team=selected_team)).order_by('-match__match_date')[:5]

        custom_matches = CustomMatch.objects.filter(Q(user_team=selected_team),is_fixture=True).order_by('match_date')[:5]
        custom_results = CustomMatchResult.objects.filter(Q(custom_match__user_team=selected_team)).order_by('-custom_match__match_date')[:5]

        player_stats = PlayerStat.objects.filter(match__in=Subquery(team_results.values("match")[:3]), player_contract__team=selected_team)
        custom_player_stats = CustomMatchPlayerStat.objects.filter(custom_match__in=Subquery(custom_results.values("custom_match")[:3]), player_contract__team=selected_team)

        # Group player stats by match
        matches_stats = {}
        matches_stats = self.group_stats(matches_stats, player_stats, False)
        matches_stats = self.group_stats(matches_stats, custom_player_stats, True)

        return {
            "contracts": latest_contracts,
            "upcoming_matches": upcoming_matches,
            "custom_matches": custom_matches,
            "team_results": team_results,
            "custom_results": custom_results,
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
            if hasattr(user, 'player'):
                selected_team = self.get_valid_team(user.player.teams, None)
            if hasattr(user, 'player'):
                selected_team = user.coach.team
        
        # team_stats = player.playerstat_set.filter(team=selected_team)

        if request.headers.get('HX-Request'):
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
            custommatch_list = CustomMatchResult.objects.filter(Q(custom_match__user_team=team)).order_by('-custom_match__match_date')

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


class CoachCreateView(LoginRequiredMixin, AdminRequiredMixin, generic.CreateView):
    template_name = "teams/coach_create.html"
    form_class = CoachModelForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CoachCreateView, self).get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CoachCreateView, self).get_context_data(**kwargs)
        admin = get_object_or_404(Admin, user=self.request.user)
        context = {'admin_teams': Team.objects.filter(admin=admin),
        'admin_team_id': self.get_selected_team_id(),
        'form': CoachModelForm(user=self.request.user)
        }

        return context

    def get_selected_team_id(self):
        selected_team_id = self.request.session.get('admin_team_id')
        request_user = self.request.user

        if selected_team_id is None:
            if hasattr(request_user, 'admin'):
                admin = get_object_or_404(Admin, user=request_user)
                teams = Team.objects.filter(admin=admin)
                if teams.exists():
                    selected_team_id = teams.first().id
                    self.request.session['admin_team_id'] = selected_team_id
            else:
                messages.error(self.request, "Action not permitted! Must be a coach")
                return render(self.request, 'landing_page')

        return selected_team_id
    
    def get_success_url(self):
        return reverse("teams:team-dashboard")
    
    def form_valid(self, form):
        fake = Faker()
        random_password = f"{random.randint(0, 100000)}"
        user = User.objects.create_user(
            username=form.cleaned_data.get('username'),
            email=form.cleaned_data.get('email'), 
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            password=random_password
        )
        user.is_coach = True
        user.save()

        # Create the Player object
        coach = form.save(commit=False)
        # player.user = user
        coach.save()

        # Get the selected team ID from the session or form
        selected_team_id = self.get_selected_team_id()
        if selected_team_id:
            selected_team = get_object_or_404(Team, id=selected_team_id)
            coach.team.add(selected_team)
        return super(CoachCreateView, self).form_valid(form)


class TeamSelectView(LoginRequiredMixin, AdminRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        selected_team_id = request.POST.get('team')
        request.session['admin_team_id'] = selected_team_id
        return redirect('teams:coach-create')
    
