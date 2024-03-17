from django.shortcuts import render, reverse
from django.views import generic
from django.utils import timezone
import datetime

from players.models import Match, Result, PlayerStat, MatchEvent
from .forms import MatchModelForm, MatchEventFormSet, MatchEventModelForm


# Create your views here.
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

    # def get_queryset(self):
    #     queryset = Match.objects.all()

    #     return queryset

    def get_form_kwargs(self, **kwargs):
        kwargs = super(MatchCreateEventView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "slug": self.kwargs['slug']
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MatchCreateEventView, self).get_context_data(**kwargs)
        match_instance = Match.objects.get(slug=self.kwargs['slug'])
        
        context['match'] = match_instance
        if self.request.POST:
            context['formset'] = MatchEventFormSet(
                self.request.POST, 
                prefix='matchevents',
                form_kwargs={'slug': self.kwargs['slug']})
        else:
            context['formset'] = MatchEventFormSet(
                prefix='matchevents',
                form_kwargs={'slug': self.kwargs['slug']}, 
                instance=match_instance)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))   

    def get_success_url(self):
        return reverse("matches:match-list")