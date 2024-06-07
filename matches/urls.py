from django.urls import path
from .views import (
    MatchListView,
    MatchDetailView,
    MatchCreateView,
    MatchCreateEventView,
    ResultCreateView,
    PlayerStatCreateEventView,
    CustomMatchCreateView,
    CustomMatchDetailView,
    )

"""
BASE ENDPOINT /matches
"""
app_name = "matches"

urlpatterns = [
    path("", MatchListView.as_view(), name='match-list'),
    path("create/", MatchCreateView.as_view(), name='match-create'),
    path("create-custom/", CustomMatchCreateView.as_view(), name='custom-match-create'),
    path("private-game/<slug:slug>/", CustomMatchDetailView.as_view(), name='custommatch-detail'),
    path("create-event/<slug:slug>/", MatchCreateEventView.as_view(), name='match-event-create'),
    path("confirm-result/<slug:slug>/", ResultCreateView.as_view(), name='result-create'),
    path("create-player-stat/<slug:slug>/", PlayerStatCreateEventView.as_view(), name='player-stat-create'),
    path("<slug:slug>/", MatchDetailView.as_view(), name='match-detail'),
]