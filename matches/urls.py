from django.urls import path
from .views import (
    MatchListView,
    MatchDetailView,
    MatchCreateView,
    MatchCreateEventView,
    ResultCreateView,
    PlayerStatCreateEventView,
    )

"""
BASE ENDPOINT /matches
"""
app_name = "matches"

urlpatterns = [
    path("", MatchListView.as_view(), name='match-list'),
    path("create/", MatchCreateView.as_view(), name='match-create'),
    path("create-event/<slug:slug>/", MatchCreateEventView.as_view(), name='match-event-create'),
    path("confirm-result/<slug:slug>/", ResultCreateView.as_view(), name='result-create'),
    path("create-player-stat/<slug:slug>/", PlayerStatCreateEventView.as_view(), name='player-stat-create'),
    path("<slug:slug>/", MatchDetailView.as_view(), name='match-detail'),
]