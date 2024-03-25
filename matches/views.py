from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.db import transaction

from players.models import (
    Match,
    Result,
    PlayerStat,
    MatchEvent,
    Player,
    )
from .forms import (
    MatchModelForm,
    MatchEventFormSet,
    MatchEventModelForm,
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
            team =self.get_object().home_team
        )
        away_team = PlayerStat.objects.filter(
            match=self.get_object(),
            team =self.get_object().away_team
        )
        context.update({
            "hometeam_players": home_team,
            "awayteam_players": away_team
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
        queryset = Match.objects.filter(slug=self.kwargs['slug'])
        return queryset
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(MatchCreateEventView, self).get_form_kwargs(**kwargs)
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
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        match_instance = Match.objects.get(slug=self.kwargs['slug'])
        formset = MatchEventFormSet(
                prefix='matchevents',
                form_kwargs={'slug': self.kwargs['slug']},
                instance=match_instance,
                queryset=MatchEvent.objects.none()
                )

        return self.render_to_response(
            self.get_context_data(form=form, formset=formset))
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        match_instance = Match.objects.get(slug=self.kwargs['slug'])
        if form.is_valid():
            self.object = form.save(commit=False)
        formset = MatchEventFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                prefix='matchevents',
                instance=match_instance,
                form_kwargs={'slug': self.kwargs['slug']},
                )
        if (form.is_valid and formset.is_valid()):
            return self.form_valid(form, formset, match_instance)
        else:
            return self.form_invalid(form, formset)
    
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
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset))
    
    def get_context_data(self, **kwargs):
        data = super(MatchCreateEventView, self).get_context_data(**kwargs)
        match_instance = Match.objects.get(slug=self.kwargs['slug'])
        data = {'match': match_instance,
                'events': MatchEvent.objects.filter(match=match_instance)
                }

        if self.request.POST:
            data['formset'] = MatchEventFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=match_instance,
                form_kwargs={'slug': self.kwargs['slug']},
                prefix = 'matchevents'
                )
        else:
            data['formset'] =  MatchEventFormSet(
                queryset=MatchEvent.objects.none(),
                instance=match_instance,
                form_kwargs={'slug': self.kwargs['slug']},
                prefix = 'matchevents'
                )
        
        return data
    

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
        context = self.get_context_data()
        Result.objects.create(
            match=context["match"], 
            score_hometeam=context["hometeam_score"], 
            score_awayteam=context["awayteam_score"]
            )
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        data = super(ResultCreateView, self).get_context_data(**kwargs)
        match_instance = Match.objects.get(slug=self.kwargs['slug'])
        home_team_players = Player.objects.filter(teams=match_instance.home_team)
        away_team_players = Player.objects.filter(teams=match_instance.away_team)
        goal_events = MatchEvent.objects.filter(match=match_instance, event_type="GOAL")
        hometeam_score = goal_events.filter(player__in=home_team_players).count()
        awayteam_score = goal_events.filter(player__in=away_team_players).count()
        data = {'match': match_instance,
                'hometeam_score': hometeam_score,
                'awayteam_score': awayteam_score
                }
        return data
