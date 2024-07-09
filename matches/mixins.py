from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404
from players.models import Player, Coach, Team


class SessionDefaultsMixin:
    def set_session_defaults(self, request):
        user_teams = self.get_user_teams()
        if not user_teams.exists():
            return self.handle_no_permission()
        if 'selected_team_id' not in request.session:
            request.session['selected_team_id'] = user_teams.first().id
        if 'match_type' not in request.session:
            request.session['match_type'] = 'home'


class UserTeamMixin(LoginRequiredMixin):
    def get_user_teams(self):
        request_user=self.request.user
        if hasattr(request_user, 'coach'):
            coach = get_object_or_404(Coach, user=request_user)
            return Team.objects.filter(slug=coach.team.slug)
        else:
            messages.error(self.request, "Action not permitted!")
            return render(self.request, 'landing_page')
        
    
    def get_selected_team(self):
        team_id = self.request.POST.get('team_id') or self.request.GET.get('team_id')
        user_teams = self.get_user_teams()
        if team_id:
            return get_object_or_404(user_teams, id=team_id)
        return user_teams.first()
