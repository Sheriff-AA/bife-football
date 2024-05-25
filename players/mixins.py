from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class CoachAndLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is player or coach"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_coach:
            return redirect("players:player-list")
        return super().dispatch(request, *args, **kwargs)