from django import forms
from .models import Player, Team, User


class PlayerModelForm(forms.ModelForm):
    # username = forms.CharField(max_length=20, required=True, label="Player's Username")
    # email = forms.CharField(max_length=45, required=True, label="Email")

    class Meta:
        model = Player
        fields = ("first_name", "last_name", "shirt_number", "age", "position")
    # teams = forms.ModelChoiceField(queryset=Team.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(PlayerModelForm, self).__init__(*args, **kwargs)
        

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

