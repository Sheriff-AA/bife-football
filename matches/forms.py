from django import forms
from players.models import Player, Match, MatchEvent, PlayerStat
from .widgets import DateTimePickerInput
from django.forms.models import inlineformset_factory
from django.db.models import Q
from django.db.models import Avg, Count, Min, Sum, Max
from django.contrib.auth.forms import UserCreationForm, UsernameField


class MatchModelForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ("home_team", "away_team", "venue", "date")
        widgets = {
            "date": DateTimePickerInput()
        }

        # def __init__(self, *args, **kwargs):
        #     request = kwargs.pop("request")
        #     team = Team.objects.filter(organisation=request.user)
        #     super(PlayerModelForm, self).__init__(*args, **kwargs)
        #     self.fields["teams"].queryset = team


class MatchEventModelForm(forms.ModelForm):
    class Meta:
        model = MatchEvent
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        match = Match.objects.get(slug=kwargs.pop("slug"))

        player = Player.objects.filter(Q(teams=match.home_team) | Q(teams=match.away_team))
        super(MatchEventModelForm, self).__init__(*args, **kwargs)
        self.fields["player"].queryset = player
        self.fields["related_player"].queryset = player


MatchEventFormSet = inlineformset_factory(
    Match, MatchEvent, form=MatchEventModelForm, extra=1, can_delete=False)


class PlayerStatModelForm(forms.ModelForm):
    class Meta:
        model = PlayerStat
        fields = ("player", "goals", "assists", "minutes_played", "rating")

    def __init__(self, *args, **kwargs):
        match = Match.objects.get(slug=kwargs.pop("slug"))
        # Filter for players that have signed a contract for each team
        # Then filter for the latest contract for each players
        player = Player.objects.filter(Q(teams=match.home_team) | Q(teams=match.away_team))
        super(PlayerStatModelForm, self).__init__(*args, **kwargs)
        self.fields["player"].queryset = player


PlayerStatFormSet = inlineformset_factory(
    Match, PlayerStat, form=PlayerStatModelForm, extra=1, can_delete=False)
