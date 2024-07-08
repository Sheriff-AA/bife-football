from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.shortcuts import redirect


class CoachRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a coach"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_coach:
            messages.error(self.request, "User is not a coach")
            return redirect("players:player-list")
        return super().dispatch(request, *args, **kwargs)
    

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an admin."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class PlayerRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a player."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_player:
            return self.handle_no_permission() # redirect to a login page
        return super().dispatch(request, *args, **kwargs)