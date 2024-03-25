from django.urls import path
from .views import (
    TeamListView,
    TeamCreateView
    )

"""
BASE ENDPOINT /teams
"""
app_name = "teams"

urlpatterns = [
    path("", TeamListView.as_view(), name='team-list'),
    path("create/", TeamCreateView.as_view(), name='team-create'),
    # path("create-event/<slug:slug>/", MatchCreateEventView.as_view(), name='match-event-create'),
    # path("confirm-result/<slug:slug>/", ResultCreateView.as_view(), name='result-create'),
    # path("<slug:slug>/", MatchDetailView.as_view(), name='match-detail'),
]