import random
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from faker import Faker
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q

from .mixins import CoachRequiredMixin, AdminRequiredMixin
from .models import Player, PlayerStat, Contract, MatchEvent, Coach, Team, User
from .forms import PlayerModelForm, PlayerModelUpdateForm, PlayerTeamForm
from custommatches.models import CustomMatchPlayerStat, CustomMatchEvent


class LandingPageView(generic.TemplateView):
    template_name = "landing_page.html"


class PlayerListView(generic.ListView):
    template_name = "players/player_list.html"
    context_object_name = "players"

    def get_queryset(self):
        return Player.objects.all().order_by('id')
    
    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
        qs = self.get_queryset()
        if search:
            qs = self.get_queryset().filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))

        paginator = Paginator(qs, 15)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        if request.htmx:
            return render(request, 'players/partials/partial_player_list.html', {'page_obj': page_obj})
        else:
            return render(request, 'players/player_list.html', {'page_obj': page_obj})


class PlayerMatchesListView(generic.DetailView):
    template_name = "players/players_matches.html"
    context_object_name = "player"

    def get_queryset(self):
        queryset = Player.objects.all()

        return queryset
    
    def get_context_data(self, **kwargs):
        player = Player.objects.get(slug=self.kwargs['slug'])
        context = super(PlayerMatchesListView, self).get_context_data(**kwargs)
        queryset = PlayerStat.objects.filter(player=self.get_object())
        custom_qs = CustomMatchPlayerStat.objects.filter(player=player)
        context.update({
            "stats": queryset,
            "custom_qs": custom_qs
        })

        return context
    

class PlayerDetailView(generic.DetailView):
    template_name = "players/player_detail.html"
    context_object_name = "player"

    def get_queryset(self):
        return Player.objects.all()
    
    def get_context_data(self, **kwargs):
        request_user = self.request.user
        player = Player.objects.get(slug=self.kwargs['slug'])
        context = super(PlayerDetailView, self).get_context_data(**kwargs)
        contract = Contract.objects.filter(is_valid=True, player=self.get_object()).order_by('-contract_date').first()
        latest_events = MatchEvent.objects.filter(player_contract=contract).order_by('-timestamp')[:5]
        custom_events = CustomMatchEvent.objects.filter(player_contract=contract).order_by('-timestamp')[:5]
        queryset = PlayerStat.objects.filter(player=self.get_object())
        custom_qs = CustomMatchPlayerStat.objects.filter(player=player)

        custom_stats = custom_qs.aggregate(
                goals = Sum('goals', default=0),
                assists = Sum('assists', default=0),
                minutes_played = Sum('minutes_played', default=0),
                games = Count("custom_match")),
        
        context.update({
            "stats": queryset.aggregate(
                goals = Sum('goals', default=0) + custom_stats[0]["goals"],
                assists = Sum('assists', default=0) + custom_stats[0]["assists"],
                minutes_played = Sum('minutes_played', default=0) + custom_stats[0]["minutes_played"],
                games = Count("match") + custom_stats[0]["games"]
                ),
            "contract": contract,
            "latest_events": latest_events,
            "custom_events": custom_events
        })

        if hasattr(request_user, 'coach'):
            coach_team = Team.objects.get(coach__user=request_user)
            if contract.team  ==  coach_team:
                player_obj = Player.objects.get(id=contract.player.id, teams=coach_team)
                if not player_obj.teams.filter(coach__user=self.request.user).exists():
                    messages.error(self.request, "Player is not part of your team")
                context["is_coach_player"] = True
            else:
                context["is_coach_player"] = False
        else:
            messages.error(self.request, "View details only")
            context["is_coach_player"] = False
        
        return context
    

class PlayerCreateView(LoginRequiredMixin, CoachRequiredMixin, generic.CreateView):
    template_name = "players/player_create.html"
    form_class = PlayerModelForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(PlayerCreateView, self).get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PlayerCreateView, self).get_context_data(**kwargs)
        coach = get_object_or_404(Coach, user=self.request.user)
        context = {'coach_teams': Team.objects.filter(coach=coach),
        'coach_team_id': self.get_selected_team_id(),
        'form': PlayerModelForm(user=self.request.user)
        }

        return context

    def get_selected_team_id(self):
        selected_team_id = self.request.session.get('coach_team_id')
        request_user = self.request.user

        if selected_team_id is None:
            if hasattr(request_user, 'coach'):
                coach = get_object_or_404(Coach, user=request_user)
                teams = Team.objects.filter(coach=coach)
                if teams.exists():
                    selected_team_id = teams.first().id
                    self.request.session['coach_team_id'] = selected_team_id
            else:
                messages.error(self.request, "Action not permitted! Must be a coach")
                return render(self.request, 'landing_page')

        return selected_team_id
    
    def get_success_url(self):
        return reverse("players:player-list")
    
    def form_valid(self, form):
        # fake = Faker()
        random_password = f"{random.randint(0, 100000)}"
        user = User.objects.create_user(
            username=form.cleaned_data.get('username'), 
            first_name=form.cleaned_data.get('first_name'),
            last_name=form.cleaned_data.get('last_name'),
            password=random_password
        )
        user.is_player = True
        user.save()

        # Create the Player object
        player = form.save(commit=False)
        player.user = user
        player.save()

        # Get the selected team ID from the session or form
        selected_team_id = self.get_selected_team_id()
        if selected_team_id:
            selected_team = get_object_or_404(Team, id=selected_team_id)
            player.teams.add(selected_team)
        return super(PlayerCreateView, self).form_valid(form)


class TeamSelectView(LoginRequiredMixin, CoachRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        selected_team_id = request.POST.get('team')
        request.session['coach_team_id'] = selected_team_id
        return redirect('players:player-create')
    

class PlayerUpdateView(LoginRequiredMixin, CoachRequiredMixin, generic.UpdateView):
    template_name = "players/player_update.html"
    form_class = PlayerModelUpdateForm
    context_object_name = "player"

    def get_queryset(self):
        player = Player.objects.filter(slug=self.kwargs.get('slug'))
        return player
        
    def get_object(self, queryset=None):
        """
        Override get_object to ensure the coach is part of the player's team.
        """
        obj = Player.objects.get(slug=self.kwargs.get('slug'))
        if not obj.teams.filter(coach__user=self.request.user).exists():
            raise PermissionDenied("You do not have permission to update this player.")
        return obj
        
    def get_success_url(self):
        return reverse("players:player-detail", kwargs={'slug': self.object.slug})
    

class PlayerDeleteView(LoginRequiredMixin, CoachRequiredMixin, generic.DeleteView):
    template_name = "players/player_delete.html"
    context_object_name = "player"
    
    def get_queryset(self):
        user = self.request.user
        # initial queryset of players for entire team  
        return Player.objects.all()     
        # return Player.objects.filter(teams=user)

    def get_success_url(self):
        return reverse("players:player-list")
    

class PlayerUpdateTeamsView(LoginRequiredMixin, CoachRequiredMixin, generic.UpdateView):
    model = Player
    form_class = PlayerTeamForm
    template_name = 'players/player_update_teams.html'
    
    def form_valid(self, form):
        player = form.save(commit=False)
        player.teams.set(form.cleaned_data['teams'])
        player.save()
        return redirect('players:player-detail', slug=player.slug)

    def get_success_url(self):
        return reverse('players:player-detail', kwargs={'slug': self.object.slug})