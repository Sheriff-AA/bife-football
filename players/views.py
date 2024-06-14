import random
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import generic
from faker import Faker
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from .mixins import CoachAndLoginRequiredMixin

from .models import Player, PlayerStat, Contract, MatchEvent, Coach, Team, User
from .forms import PlayerModelForm, PlayerModelUpdateForm, PlayerTeamForm


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
        contract = Contract.objects.filter(is_valid=True, player=self.get_object()).first()
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
    

class PlayerCreateView(CoachAndLoginRequiredMixin, generic.CreateView):
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
        'coach_team_id': self.get_selected_team_id()
        }

        return context

    def get_selected_team_id(self):
        selected_team_id = self.request.session.get('coach_team_id')

        if selected_team_id is None:
            coach = get_object_or_404(Coach, user=self.request.user)
            teams = Team.objects.filter(coach=coach)
            if teams.exists():
                selected_team_id = teams.first().id
                self.request.session['coach_team_id'] = selected_team_id

        return selected_team_id
    
    def get_success_url(self):
        return reverse("players:player-list")
    
    def form_valid(self, form):
        fake = Faker()
        random_password = f"{random.randint(0, 100000)}"
        user = User.objects.create_user(
            username=fake.user_name(),  # Generate a random username
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


class TeamSelectView(CoachAndLoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        selected_team_id = request.POST.get('team')
        request.session['coach_team_id'] = selected_team_id
        return redirect('players:player-create')
    

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
    

class PlayerUpdateTeamsView(generic.UpdateView):
    model = Player
    form_class = PlayerTeamForm
    template_name = 'players/player_update_teams.html'
    
    def form_valid(self, form):
        player = form.save(commit=False)
        player.teams.set(form.cleaned_data['teams'])
        player.save()
        return redirect('players:player-detail', pk=player.slug)

    def get_success_url(self):
        return reverse('players:player-detail', kwargs={'slug': self.object.slug})