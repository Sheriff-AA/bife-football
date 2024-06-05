from django import forms
from players.models import Team, Player, Coach


class TeamModelForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class TeamSelectForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=True, label="Select Team")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TeamSelectForm, self).__init__(*args, **kwargs) 
        # Check if obj is an instance of the Player or Coach model       
        if isinstance(user, Player):
            self.fields['team'].queryset = user.teams.all()
        if isinstance(user, Coach):
            self.fields['team'].queryset = Team.objects.filter(slug=user.team.slug)