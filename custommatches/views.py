from django.shortcuts import reverse, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.conf import settings
from django.views import generic

from players.models import Contract
from .models import CustomMatch, CstmMatchPlayerStat, CstmMatchResult, CstmMatchEvent
from .forms import CstmMatchModelForm, CustomMatchEventFormSet, CstmMatchPlayerStatModelForm, CstmMatchPlayerStatFormSet, CstmCreateResultForm, CstmMatchEventModelForm

GET_LATEST_CONTRACTS = settings.GET_LATEST_CONTRACTS


# Create your views here.
class CstmMatchCreateView(generic.CreateView):
    template_name = "custommatches/cstmmatch_create.html"
    form_class = CstmMatchModelForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def get_success_url(self):
        return reverse("matches:match-list")
    
    def form_valid(self, form):
        match = form.save(commit=False)
        # match.is_home = form.cleaned_data['is_home']
        match.save()
        return super(CstmMatchCreateView, self).form_valid(form)
    

class CstmMatchDetailView(generic.DetailView):
    template_name = "custommatches/cstmmatch_detail.html"
    context_object_name = "match"

    def get_queryset(self):
        queryset = CustomMatch.objects.all()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(CstmMatchDetailView, self).get_context_data(**kwargs)
        user_team = CstmMatchPlayerStat.objects.filter(
            custom_match=self.get_object(),
            player_contract__team =self.get_object().user_team
        )

        context.update({
            "userteam_players": user_team,
            "events": self.get_object().cstmmatchevent_set.all()
        })
        return context


class CstmMatchCreateEventView(generic.CreateView):
    template_name = "custommatches/cstmmatch_create_event.html"
    form_class = CstmMatchEventModelForm

    def get_queryset(self):
        return CustomMatch.objects.filter(slug=self.kwargs['slug'])

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
            'events': match_instance.cstmmatchevent_set.all()
        })
        if self.request.POST:
            data['formset'] = self.get_formset(match_instance)
        else:
            data['formset'] = CustomMatchEventFormSet(
                queryset=CstmMatchEvent.objects.none(),
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
        return CustomMatchEventFormSet(
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
                return redirect("custommatches:custom-create-result", slug=instance.slug)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(form=form, formset=formset))    


class CstmResultCreateView(generic.CreateView):
    template_name = "custommatches/cstmmatch_create_result.html"
    form_class = CstmCreateResultForm

    def get_queryset(self):
        queryset = CustomMatch.objects.filter(slug=self.kwargs['slug'])
        return queryset

    def get_success_url(self):
        return reverse("matches:match-list")
    
    def form_valid(self, form):
        match_instance = self.get_object()
        CstmMatchResult.objects.create(
            custom_match=match_instance, 
            score_userteam = self.calculate_score(match_instance.user_team),
            score_versusteam = form.cleaned_data['score_versusteam']
            )
        
        return redirect("custommatches:custom-playerstat-create", slug=match_instance.slug)
        
    
    def get_context_data(self, **kwargs):
        data = super(CstmResultCreateView, self).get_context_data(**kwargs)
        match_instance = self.get_object()
        data = {'match': match_instance,
                'userteam_score': self.calculate_score(match_instance.user_team),
                'form': CstmCreateResultForm()
                }
        return data
    
    def calculate_score(self, team):
        player_contracts = self.get_latest_contracts(team)
        goal_events = CstmMatchEvent.objects.filter(
            player_contract__in=player_contracts,
            custom_match=self.get_object(),
            event_type="GOAL",
        )
        return goal_events.count()
    
    def get_latest_contracts(self, team):
        contracts = Contract.objects.filter(team=team)
        return contracts.extra(
            where=[GET_LATEST_CONTRACTS]
        )


class CstmMatchPlayerStatCreateEventView(generic.CreateView):
    template_name = "custommatches/cstmmatch_create_playerstats.html"
    form_class = CstmMatchPlayerStatModelForm

    def get_queryset(self):
        return CustomMatch.objects.filter(slug=self.kwargs['slug'])
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(CstmMatchPlayerStatCreateEventView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "slug": self.kwargs['slug']
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        data = super(CstmMatchPlayerStatCreateEventView, self).get_context_data(**kwargs)
        data["match"] = self.get_match_instance()
        data['formset'] = self.get_formset(data['match'], form_kwargs={'slug': self.kwargs['slug']})
        
        return data
    
    def get_match_instance(self):
        return get_object_or_404(self.get_queryset())
    
    def get_formset(self, match_instance, *args, **kwargs):
        prefix = kwargs.pop('prefix', 'playerstats')
        formset = CstmMatchPlayerStatFormSet(*args, **kwargs, prefix=prefix, instance=match_instance)
    
        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match_instance.user_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        
        initial_data = [{'player_contract': contract} for contract in latest_contracts]
        for form, initial in zip(formset.forms, initial_data):
            form.initial.update(initial)

        return formset
        
    def get_success_url(self):
        return reverse("matches:match-list")
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        match_instance = self.get_match_instance()
        formset = self.get_formset(match_instance, form_kwargs={'slug': self.kwargs['slug']})

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
    
