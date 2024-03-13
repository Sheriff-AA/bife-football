from django import forms
from players.models import Player, Team, Match
from .widgets import DateTimePickerInput
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

class PlayerModelUpdateForm(forms.ModelForm):
    class Meta:
        model = Player
        fields =("first_name", "last_name", "shirt_number", "age", "position")