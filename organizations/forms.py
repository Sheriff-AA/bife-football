from allauth.account.forms import SignupForm
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect
from django import forms
from players.models import Team, Coach

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=20, required=True, label='First Name')
    last_name = forms.CharField(max_length=20, required=True, label='Last Name')
    team_name = forms.CharField(max_length=80, required=True, label='Name of Your Team')
    short_team_name = forms.CharField(max_length=3, required=True, label='Abbreviated 3 Letter Name For Your Team')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.is_coach = True
        user.save()
        try:
            team = Team.objects.create(
            team_name = self.cleaned_data['team_name'],
            short_team_name = self.cleaned_data['short_team_name'],
            organisation = user
        )
        except IntegrityError as e:
            messages.error(request, "Action not permitted by user")
        Coach.objects.create(
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            team = team,
            user = user
        )
        return user