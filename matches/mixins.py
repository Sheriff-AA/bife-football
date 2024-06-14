from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from players.models import Player


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
        # Assuming the User model has a related_name 'teams' for related teams
        user = get_object_or_404(Player, user=self.request.user)
        return user.teams.filter(contract__is_valid=True)

    def get_selected_team(self):
        team_id = self.request.POST.get('team_id') or self.request.GET.get('team_id')
        user_teams = self.get_user_teams()
        if team_id:
            return get_object_or_404(user_teams, id=team_id)
        return user_teams.first()
