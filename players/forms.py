from django import forms
from .models import Player, Team
from django.contrib.auth.forms import UserCreationForm, UsernameField


class PlayerModelForm(forms.ModelForm):
    class Meta:
        model = Player
        fields =("first_name", "last_name", "shirt_number", "age", "position", "teams")
        teams = forms.ModelChoiceField(queryset=Team.objects.all())

        # def __init__(self, *args, **kwargs):
        #     request = kwargs.pop("request")
        #     team = Team.objects.filter(organisation=request.user)
        #     super(PlayerModelForm, self).__init__(*args, **kwargs)
        #     self.fields["teams"].queryset = team

        
class PlayerModelUpdateForm(forms.ModelForm):
    class Meta:
        model = Player
        fields =("first_name", "last_name", "shirt_number", "age", "position")


class PlayerTeamForm(forms.ModelForm):
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    
    class Meta:
        model = Player
        fields = ['teams']

    def __init__(self, *args, **kwargs):
        super(PlayerTeamForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['teams'].initial = self.instance.teams.all()