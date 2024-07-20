from django.core.exceptions import ValidationError
from django import forms


from players.models import Team, Player, Coach, User


class TeamModelForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class CoachModelForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True, label="Coach's Username")
    email = forms.CharField(max_length=45, required=True, label="Email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists.')
        return email
    
    class Meta:
        model = Coach
        fields = ("first_name", "last_name")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(CoachModelForm, self).__init__(*args, **kwargs)


class TeamSelectForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=True, label="Select Team")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TeamSelectForm, self).__init__(*args, **kwargs) 
        # Check if obj is an instance of the Player or Coach model       
        if hasattr(user, 'player'):
            self.fields['team'].queryset = user.player.teams.filter(contract__is_valid=True)
        if hasattr(user, 'coach'):
            self.fields['team'].queryset = Team.objects.filter(slug=user.coach.team.slug)