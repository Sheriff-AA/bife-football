from django.shortcuts import reverse, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from players.models import Contract
from players.mixins import AdminorCoachRequiredMixin, CoachRequiredMixin
from .models import CustomMatch, CustomMatchPlayerStat, CustomMatchResult, CustomMatchEvent
from .forms import CustomMatchModelForm, CustomMatchEventFormSet, CustomMatchPlayerStatModelForm, CustomMatchPlayerStatFormSet, CustomCreateResultForm, CustomMatchEventModelForm

GET_LATEST_CONTRACTS = settings.GET_LATEST_CONTRACTS


# Create your views here.
class CustomMatchCreateView(LoginRequiredMixin, CoachRequiredMixin, generic.CreateView):
    template_name = "custommatches/cstmmatch_create.html"
    form_class = CustomMatchModelForm

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
        match.save()
        return super(CustomMatchCreateView, self).form_valid(form)
    

class CustomMatchDetailView(generic.DetailView):
    template_name = "custommatches/cstmmatch_detail.html"
    context_object_name = "match"

    def get_queryset(self):
        queryset = CustomMatch.objects.all()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(CustomMatchDetailView, self).get_context_data(**kwargs)
        can_edit_stats = False
        user_team = CustomMatchPlayerStat.objects.filter(
            custom_match=self.get_object(),
            player_contract__team =self.get_object().user_team
        )
        if hasattr(self.request.user, 'coach'):
            if self.request.user.coach.team == self.get_object().user_team:
                can_edit_stats = True

        context.update({
            "userteam_players": user_team,
            "can_edit_stats": can_edit_stats,
            "events": self.get_object().match_events.all().order_by('minute')
        })
        return context


class CustomMatchCreateEventView(LoginRequiredMixin, AdminorCoachRequiredMixin, generic.CreateView):
    template_name = "custommatches/cstmmatch_create_event.html"
    form_class = CustomMatchEventModelForm

    def get_queryset(self):
        return CustomMatch.objects.filter(slug=self.kwargs['slug'])

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"slug": self.kwargs['slug']})
        return kwargs

    def get_success_url(self):
        return reverse("custommatches:custommatch-detail", kwargs={'slug':self.kwargs['slug']})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        match_instance = self.get_queryset().get()
        request_user = self.request.user
        data.update({
            'match': match_instance,
            'events': match_instance.match_events.all().order_by('minute')
        })
        if self.request.POST:
            data['formset'] = self.get_formset(match_instance)
            if hasattr(request_user, 'admin'):
                # messages.error(self.request, "Admin allowed")
                admin_team = request_user.admin.team
                if admin_team == match_instance.user_team:
                    data["can_add_event"] = True
                else:
                    data["can_add_event"] = False
            elif hasattr(request_user, 'coach'):
                # messages.error(self.request, "Admin allowed")
                coach_team = request_user.coach.team
                if coach_team == match_instance.user_team:
                    data["can_add_event"] = True
                else:
                    data["can_add_event"] = False
            else:
                # messages.error(self.request, "View details only")
                data["can_add_event"] = False
        else:
            data['formset'] = CustomMatchEventFormSet(
                queryset=CustomMatchEvent.objects.none(),
                instance=match_instance,
                form_kwargs={'slug': self.kwargs['slug']},
                prefix='matchevents'
            )
            if hasattr(request_user, 'admin'):
                # messages.error(self.request, "Admin allowed")
                admin_team = request_user.admin.team
                if admin_team == match_instance.user_team:
                    data["can_add_event"] = True
                else:
                    data["can_add_event"] = False
            elif hasattr(request_user, 'coach'):
                # messages.error(self.request, "Admin allowed")
                coach_team = request_user.coach.team
                if coach_team == match_instance.user_team:
                    data["can_add_event"] = True
                else:
                    data["can_add_event"] = False
            else:
                # messages.error(self.request, "View details only")
                data["can_add_event"] = False
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
            if match_event.event_type == "FULLTIME":
                instance.match_events.filter(event_type="FULLTIME").delete()
                instance.is_fixture = False
                instance.save()
                match_event.save()
                # return redirect("custommatches:custom-create-result", slug=instance.slug)
                return HttpResponseRedirect(self.get_success_url())
            else:
                match_event.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(self.get_context_data(form=form, formset=formset))    


class CustomResultCreateView(LoginRequiredMixin, AdminorCoachRequiredMixin, generic.CreateView):
    template_name = "custommatches/cstmmatch_create_result.html"
    form_class = CustomCreateResultForm

    def get_queryset(self):
        queryset = CustomMatch.objects.filter(slug=self.kwargs['slug'])
        return queryset

    def get_success_url(self):
        return reverse("custommatches:custommatch-detail", kwargs={'slug':self.kwargs['slug']})
    
    def form_valid(self, form):
        match_instance = self.get_object()
        CustomMatchResult.objects.create(
            custom_match=match_instance, 
            score_userteam = self.calculate_score(match_instance.user_team),
            score_versusteam = form.cleaned_data['score_versusteam']
            )
        match_instance.has_result=True
        match_instance.save()
        
        return HttpResponseRedirect(self.get_success_url())
        
    
    def get_context_data(self, **kwargs):
        data = super(CustomResultCreateView, self).get_context_data(**kwargs)
        match_instance = self.get_object()
        data = {'match': match_instance,
                'userteam_score': self.calculate_score(match_instance.user_team),
                'form': CustomCreateResultForm()
                }
        return data
    
    def calculate_score(self, team):
        player_contracts = self.get_latest_contracts(team)
        goal_events = CustomMatchEvent.objects.filter(
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


class CustomMatchPlayerStatCreateEventView(LoginRequiredMixin, AdminorCoachRequiredMixin, generic.CreateView):
    template_name = "custommatches/cstmmatch_create_playerstats.html"
    form_class = CustomMatchPlayerStatModelForm

    def get_queryset(self):
        return CustomMatch.objects.filter(slug=self.kwargs['slug'])
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(CustomMatchPlayerStatCreateEventView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "slug": self.kwargs['slug']
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        data = super(CustomMatchPlayerStatCreateEventView, self).get_context_data(**kwargs)
        data["match"] = self.get_match_instance()
        data['formset'] = self.get_formset(data['match'], form_kwargs={'slug': self.kwargs['slug']})
        
        return data
    
    def get_match_instance(self):
        return get_object_or_404(self.get_queryset())
    
    def get_formset(self, match_instance, *args, **kwargs):
        prefix = kwargs.pop('prefix', 'playerstats')
        formset = CustomMatchPlayerStatFormSet(*args, **kwargs, prefix=prefix, instance=match_instance)
    
        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match_instance.user_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        
        initial_data = [{'player_contract': contract} for contract in latest_contracts]
        for form, initial in zip(formset.forms, initial_data):
            form.initial.update(initial)

        return formset
        
    def get_success_url(self):
        return reverse("custommatches:custommatch-detail", kwargs={'slug':self.kwargs['slug']})
    
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
    
