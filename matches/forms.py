from django import forms
from django.conf import settings
from players.models import Player, Match, MatchEvent, PlayerStat, Contract, CustomMatch, Team
from .widgets import DateTimePickerInput
from django import forms
from django.forms.models import inlineformset_factory
from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum, Max
from django.contrib.auth.forms import UserCreationForm, UsernameField


GET_LATEST_CONTRACTS = settings.GET_LATEST_CONTRACTS


class MatchModelForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ("home_team", "away_team", "venue", "match_date")
        widgets = {
            "match_date": DateTimePickerInput()
        }

    def __init__(self, *args, **kwargs):
        user_team = kwargs.pop('user_team', None)
        match_type = kwargs.pop('match_type', 'home')
        super(MatchModelForm, self).__init__(*args, **kwargs)
        if user_team:
            if match_type == 'home':
                self.fields['home_team'].queryset = Team.objects.filter(id=user_team.id)
                self.fields['away_team'].queryset = Team.objects.exclude(id=user_team.id)
            else:
                self.fields['home_team'].queryset = Team.objects.exclude(id=user_team.id)
                self.fields['away_team'].queryset = Team.objects.filter(id=user_team.id)


class CustomMatchModelForm(forms.ModelForm):
    class Meta:
        model = CustomMatch
        fields = ("versus_team", "user_team", "venue", "match_date")
        widgets = {
            "match_date": DateTimePickerInput(),
        }


class MatchEventModelForm(forms.ModelForm):
    class Meta:
        model = MatchEvent
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        match = Match.objects.get(slug=kwargs.pop("slug"))

        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.home_team) | Q(team=match.away_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        super(MatchEventModelForm, self).__init__(*args, **kwargs)
        self.fields["player_contract"].queryset = latest_contracts
        self.fields["related_player"].queryset = latest_contracts


MatchEventFormSet = inlineformset_factory(
    Match, MatchEvent, form=MatchEventModelForm, extra=1, can_delete=False)


class PlayerStatModelForm(forms.ModelForm):
    class Meta:
        model = PlayerStat
        fields = ("player_contract", "goals", "assists", "minutes_played", "rating")

    def __init__(self, *args, **kwargs):
        match = Match.objects.get(slug=kwargs.pop("slug"))
        # Filter for players that have signed a contract for each team
        # Then filter for the latest contract for each players
        contract_for_teams = Contract.objects.filter(Q(is_valid=True) & (Q(team=match.home_team) | Q(team=match.away_team)))
        latest_contracts = contract_for_teams.extra(
            where=[GET_LATEST_CONTRACTS]
        )
        super(PlayerStatModelForm, self).__init__(*args, **kwargs)
        self.fields["player_contract"].queryset = latest_contracts


PlayerStatFormSet = inlineformset_factory(
    Match, PlayerStat, form=PlayerStatModelForm, extra=1, can_delete=False)
