from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.db import IntegrityError
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms
from players.models import Team, Coach

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=20, required=True, label='First Name')
    last_name = forms.CharField(max_length=20, required=True, label='Last Name')
    team_name = forms.CharField(max_length=80, required=True, label='Name of Your Team')
    short_team_name = forms.CharField(max_length=3, required=True, label='Abbreviated 3 Letter Name For Your Team')

    def clean_team_name(self):
        team_name = self.cleaned_data.get('team_name')
        if Team.objects.filter(team_name=team_name).exists():
            raise ValidationError('A team with this name already exists.')
        return team_name

    def clean_short_team_name(self):
        short_team_name = self.cleaned_data.get('short_team_name')
        if Team.objects.filter(short_team_name=short_team_name).exists():
            raise ValidationError('A team with this abbreviated name already exists.')
        return short_team_name

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.is_coach = True
        user.save()
        team = Team.objects.create(
        team_name = self.cleaned_data['team_name'],
        short_team_name = self.cleaned_data['short_team_name'],
        organisation = user
        )
        Coach.objects.create(
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            team = team,
            user = user
        )
        return user
    

class MyCustomSocialSignupForm(SocialSignupForm):
    first_name = forms.CharField(max_length=20, required=True, label='First Name')
    last_name = forms.CharField(max_length=20, required=True, label='Last Name')
    team_name = forms.CharField(max_length=80, required=True, label='Name of Your Team')
    short_team_name = forms.CharField(max_length=3, required=True, label='Abbreviated 3 Letter Name For Your Team')

    def clean_team_name(self):
        team_name = self.cleaned_data.get('team_name')
        if Team.objects.filter(team_name=team_name).exists():
            raise ValidationError('A team with this name already exists.')
        return team_name

    def clean_short_team_name(self):
        short_team_name = self.cleaned_data.get('short_team_name')
        if Team.objects.filter(short_team_name=short_team_name).exists():
            raise ValidationError('A team with this abbreviated name already exists.')
        return short_team_name

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.is_coach = True
        user.save()
        team = Team.objects.create(
        team_name = self.cleaned_data['team_name'],
        short_team_name = self.cleaned_data['short_team_name'],
        organisation = user
        )
        Coach.objects.create(
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            team = team,
            user = user
        )
        return user