from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.db.models import Q
from django.db import transaction

from players.models import (
    Match,
    Result,
    PlayerStat,
    MatchEvent,
    Player,
    Contract,
    )
from .forms import (
    MatchModelForm,
    MatchEventFormSet,
    MatchEventModelForm,
    PlayerStatFormSet,
    PlayerStatModelForm
    )


class MatchListView(generic.ListView):
    template_name = "matches/match_list.html"
    context_object_name = "matches"

    def get_queryset(self):
        queryset = Match.objects.all()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(MatchListView, self).get_context_data(**kwargs)
        queryset = Result.objects.all()
        fixtures = Match.objects.filter(is_fixture=True)
        context.update({
            "results": queryset,
            "fixtures": fixtures
        })

        return context
    

class MatchDetailView(generic.DetailView):
    template_name = "matches/match_detail.html"
    context_object_name = "match"

    def get_queryset(self):
        queryset = Match.objects.all()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        home_team = PlayerStat.objects.filter(
            match=self.get_object(),
            player_contract__team =self.get_object().home_team
        )
        away_team = PlayerStat.objects.filter(
            match=self.get_object(),
            player_contract__team =self.get_object().away_team
        )
        context.update({
            "hometeam_players": home_team,
            "awayteam_players": away_team,
            "events": self.get_object().matchevent_set.all()
        })
        return context


class MatchCreateView(generic.CreateView):
    template_name = "matches/match_create.html"
    form_class = MatchModelForm

    def get_success_url(self):
        return reverse("matches:match-list")
    
    def form_valid(self, form):
        match = form.save(commit=False)
        if match.date < timezone.now():
            match.is_fixture = False
        match.save()
        return super(MatchCreateView, self).form_valid(form)
    

class MatchCreateEventView(generic.CreateView):
    template_name = "matches/match_event_create.html"
    form_class = MatchEventModelForm

    def get_queryset(self):
        return Match.objects.filter(slug=self.kwargs['slug'])

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"slug": self.kwargs['slug']})
        return kwargs

    def get_success_url(self):
        return reverse("matches:match-list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        match_instance = self.get_queryset().get()
        data.update({
            'match': match_instance,
            'events': match_instance.matchevent_set.all()
        })
        if self.request.POST:
            data['formset'] = MatchEventFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=match_instance,
                form_kwargs={'slug': self.kwargs['slug']},
                prefix='matchevents'
            )
        else:
            data['formset'] = MatchEventFormSet(
                queryset=MatchEvent.objects.none(),
                instance=match_instance,
                form_kwargs={'slug': self.kwargs['slug']},
                prefix='matchevents'
            )
        return data

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        # match_instance = self.get_queryset().get()
        # formset = self.get_formset(match_instance)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        valid
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        match_instance = self.get_queryset().get()
        formset = self.get_formset(match_instance)
        if formset.is_valid():
            return self.form_valid(form, formset, match_instance)
        else:
            return self.form_invalid(form, formset)

    def get_formset(self, instance):
        return MatchEventFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            prefix='matchevents',
            instance=instance,
            form_kwargs={'slug': self.kwargs['slug']},
        )

    def form_valid(self, form, formset, instance):
        """
        Called if all forms are valid. Creates a MatchEvent instance and then redirects to a success page.
        """
        match_events = formset.save(commit=False)
        for match_event in match_events:
            match_event.save()
            if match_event.event_type == "FULLTIME":
                instance.is_fixture = False
                instance.save()
                return redirect("matches:result-create", slug=instance.slug)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(form=form, formset=formset))    


class ResultCreateView(generic.CreateView):
    template_name = "matches/result_create.html"
    context_object_name = "match"
    fields = []

    def get_queryset(self):
        queryset = Match.objects.filter(slug=self.kwargs['slug'])
        return queryset

    def get_success_url(self):
        return reverse("matches:match-list")
    
    def form_valid(self, form):
        match_instance = self.get_object()
        Result.objects.create(
            match=match_instance, 
            score_hometeam=self.calculate_score(match_instance.home_team), 
            score_awayteam=self.calculate_score(match_instance.away_team)
            )
        
        return redirect("matches:player-stat-create", slug=match_instance.slug)
        
        # return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        data = super(ResultCreateView, self).get_context_data(**kwargs)
        match_instance = self.get_object()
        data = {'match': match_instance,
                'hometeam_score': self.calculate_score(match_instance.home_team),
                'awayteam_score': self.calculate_score(match_instance.away_team)
                }
        return data
    
    def calculate_score(self, team):
        player_contracts = self.get_latest_contracts(team)
        goal_events = MatchEvent.objects.filter(
            player_contract__in=player_contracts,
            match=self.get_object(),
            event_type="GOAL",
        )
        return goal_events.count()
    
    def get_latest_contracts(self, team):
        contracts = Contract.objects.filter(team=team)
        return contracts.extra(
            where=[
            '''id IN (SELECT id FROM (SELECT id, ROW_NUMBER() 
            OVER (PARTITION BY player_id ORDER BY contract_date DESC) AS rn 
            FROM players_contract) AS subquery 
            WHERE rn = 1)'''
            ]
        )


class PlayerStatCreateEventView(generic.CreateView):
    template_name = "matches/player_stats_create.html"
    form_class = PlayerStatModelForm

    def get_queryset(self):
        return Match.objects.filter(slug=self.kwargs['slug'])
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(PlayerStatCreateEventView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "slug": self.kwargs['slug']
        })
        return kwargs
        
    def get_success_url(self):
        return reverse("matches:match-list")
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        match_instance = self.get_match_instance()
        formset = self.get_formset(match_instance)

        return self.render_to_response(
            self.get_context_data(formset=formset))
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        match_instance = self.get_match_instance()
        formset = self.get_formset(match_instance,
                        request.POST or None,
                        request.FILES or None,
                        form_kwargs={'slug': self.kwargs['slug']}
                        )
        if (formset.is_valid()):
            return self.form_valid(formset, match_instance)
        else:
            return self.form_invalid(form, formset)
    
    def form_valid(self, formset, instance):
        """
        Called if all forms are valid. Creates a PlayerStat instance and then redirects to a success page.
        """
        player_stats = formset.save(commit=False)
        for player_stat in player_stats:
            player_stat.player = player_stat.player_contract.player
            player_stat.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset))
    
    def get_context_data(self, **kwargs):
        data = super(PlayerStatCreateEventView, self).get_context_data(**kwargs)
        data["match"] = self.get_match_instance()
        data['formset'] = self.get_formset(data['match'], form_kwargs={'slug': self.kwargs['slug']})
        
        return data
    
    def get_match_instance(self):
        return get_object_or_404(self.get_queryset())
    
    def get_formset(self, match_instance, *args, **kwargs):
        prefix = kwargs.pop('prefix', 'playerstats')
        return PlayerStatFormSet(*args, **kwargs, prefix=prefix, instance=match_instance)