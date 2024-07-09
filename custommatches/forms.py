from django import forms
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import CustomMatch, CustomMatchEvent, CustomMatchPlayerStat, CustomMatchResult
from players.models import Contract, Coach, Team
from matches.widgets import DateTimePickerInput

GET_LATEST_CONTRACTS = settings.GET_LATEST_CONTRACTS


class CustomMatchModelForm(forms.ModelForm):
    class Meta:
        model = CustomMatch
        fields = ("versus_team", "user_team", "venue", "match_date", "is_home")
        widgets = {
            "match_date": DateTimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('user')
        if hasattr(request_user, 'coach'):
            coach = get_object_or_404(Coach, user=request_user)
            super(CustomMatchModelForm, self).__init__(*args, **kwargs)
            self.fields['user_team'].queryset = Team.objects.filter(slug=coach.team.slug)
        else:
            messages.error(self.request, "User is not a coach")
            return render(self.request, 'landing_page')


class CustomMatchEventModelForm(forms.ModelForm):
    class Meta:
        model = CustomMatchEvent
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        match = CustomMatch.objects.get(slug=kwargs.pop("slug"))

        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.user_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        super(CustomMatchEventModelForm, self).__init__(*args, **kwargs)
        self.fields["player_contract"].queryset = latest_contracts
        self.fields["related_player"].queryset = latest_contracts


CustomMatchEventFormSet = inlineformset_factory(
    CustomMatch, CustomMatchEvent, form=CustomMatchEventModelForm, extra=1, can_delete=False)


class CustomMatchPlayerStatModelForm(forms.ModelForm):
    class Meta:
        model = CustomMatchPlayerStat
        fields = ("player_contract", "goals", "assists", "minutes_played", "rating")

    def __init__(self, *args, **kwargs):
        match = CustomMatch.objects.get(slug=kwargs.pop("slug"))
        # Filter for players that have signed a contract for each team
        # Then filter for the latest contract for each players
        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.user_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        super(CustomMatchPlayerStatModelForm, self).__init__(*args, **kwargs)
        self.fields["player_contract"].queryset = latest_contracts
        self.fields["player_contract"].disabled = True

    @staticmethod
    def get_latest_contracts(match):
        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.user_team)))
        return contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        # Contract.objects.filter(
        #     Q(is_valid=True) & 
        #     (Q(team=match.home_team) | Q(team=match.away_team))
        # ).order_by('player', '-date_signed').distinct('player')


class CustomBasePlayerStatFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.match = kwargs['instance']
        self.player_contracts = CustomMatchPlayerStatModelForm.get_latest_contracts(self.match)
        self.extra = len(self.player_contracts)
        super(CustomBasePlayerStatFormSet, self).__init__(*args, **kwargs)
        for form, contract in zip(self.forms, self.player_contracts):
            form.initial['player_contract'] = contract


CustomMatchPlayerStatFormSet = inlineformset_factory(
    CustomMatch, CustomMatchPlayerStat, form=CustomMatchPlayerStatModelForm, formset=CustomBasePlayerStatFormSet, extra=0, can_delete=False)


class CustomCreateResultForm(forms.ModelForm):
    class Meta:
        model = CustomMatchResult
        fields = ('score_versusteam',)

