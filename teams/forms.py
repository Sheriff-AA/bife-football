from django import forms
from players.models import Team


class TeamModelForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class TeamSelectForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=True, label="Select Team")

    def __init__(self, *args, **kwargs):
        player = kwargs.pop('player', None)
        super(TeamSelectForm, self).__init__(*args, **kwargs)
        if player:
            self.fields['team'].queryset = player.teams.all()