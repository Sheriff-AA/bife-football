from django import forms
from django.conf import settings
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import CustomMatch, CstmMatchEvent, CstmMatchPlayerStat, CstmMatchResult
from players.models import Contract, Player
from matches.widgets import DateTimePickerInput

GET_LATEST_CONTRACTS = settings.GET_LATEST_CONTRACTS

class CstmMatchModelForm(forms.ModelForm):
    class Meta:
        model = CustomMatch
        fields = ("versus_team", "user_team", "venue", "match_date", "is_home")
        widgets = {
            "match_date": DateTimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('user')
        user = get_object_or_404(Player, user=request_user)
        super(CstmMatchModelForm, self).__init__(*args, **kwargs)
        self.fields['user_team'].queryset = user.teams.filter(contract__is_valid=True)


class CstmMatchEventModelForm(forms.ModelForm):
    class Meta:
        model = CstmMatchEvent
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        match = CustomMatch.objects.get(slug=kwargs.pop("slug"))

        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.user_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        super(CstmMatchEventModelForm, self).__init__(*args, **kwargs)
        self.fields["player_contract"].queryset = latest_contracts
        self.fields["related_player"].queryset = latest_contracts


CustomMatchEventFormSet = inlineformset_factory(
    CustomMatch, CstmMatchEvent, form=CstmMatchEventModelForm, extra=1, can_delete=False)


class CstmMatchPlayerStatModelForm(forms.ModelForm):
    class Meta:
        model = CstmMatchPlayerStat
        fields = ("player_contract", "goals", "assists", "minutes_played", "rating")

    def __init__(self, *args, **kwargs):
        match = CustomMatch.objects.get(slug=kwargs.pop("slug"))
        # Filter for players that have signed a contract for each team
        # Then filter for the latest contract for each players
        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.user_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        super(CstmMatchPlayerStatModelForm, self).__init__(*args, **kwargs)
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


class CstmBasePlayerStatFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.match = kwargs['instance']
        self.player_contracts = CstmMatchPlayerStatModelForm.get_latest_contracts(self.match)
        self.extra = len(self.player_contracts)
        super(CstmBasePlayerStatFormSet, self).__init__(*args, **kwargs)
        for form, contract in zip(self.forms, self.player_contracts):
            form.initial['player_contract'] = contract


CstmMatchPlayerStatFormSet = inlineformset_factory(
    CustomMatch, CstmMatchPlayerStat, form=CstmMatchPlayerStatModelForm, formset=CstmBasePlayerStatFormSet, extra=0, can_delete=False)


class CstmCreateResultForm(forms.ModelForm):
    class Meta:
        model = CstmMatchResult
        fields = ('score_versusteam',)

