from django import forms
from players.models import Player, Match, MatchEvent, PlayerStat, Contract, CustomMatch
from .widgets import DateTimePickerInput
from django import forms
from django.forms.models import inlineformset_factory
from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum, Max
from django.contrib.auth.forms import UserCreationForm, UsernameField


class MatchModelForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ("home_team", "away_team", "venue", "match_date")
        widgets = {
            "match_date": DateTimePickerInput()
        }

        # def __init__(self, *args, **kwargs):
        #     request = kwargs.pop("request")
        #     team = Team.objects.filter(organisation=request.user)
        #     super(PlayerModelForm, self).__init__(*args, **kwargs)
        #     self.fields["teams"].queryset = team


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

        contract_for_teams = Contract.objects.filter(Q(team=match.home_team) | Q(team=match.away_team))
        latest_contracts = contract_for_teams.extra(
            where=[
            '''id IN (SELECT id FROM (SELECT id, ROW_NUMBER() 
            OVER (PARTITION BY player_id ORDER BY contract_date DESC) AS rn 
            FROM players_contract) AS subquery 
            WHERE rn = 1)'''
            ]
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
        contract_for_teams = Contract.objects.filter(Q(team=match.home_team) | Q(team=match.away_team))
        latest_contracts = contract_for_teams.extra(
            where=[
            '''id IN (SELECT id FROM (SELECT id, ROW_NUMBER() 
            OVER (PARTITION BY player_id ORDER BY contract_date DESC) AS rn 
            FROM players_contract) AS subquery 
            WHERE rn = 1)'''
            ]
        )
        super(PlayerStatModelForm, self).__init__(*args, **kwargs)
        self.fields["player_contract"].queryset = latest_contracts


PlayerStatFormSet = inlineformset_factory(
    Match, PlayerStat, form=PlayerStatModelForm, extra=1, can_delete=False)
