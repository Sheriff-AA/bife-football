from django import forms
from players.models import Team


class TeamModelForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"