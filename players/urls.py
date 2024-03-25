from django.urls import path
from .views import (
    PlayerListView,
    PlayerDetailView,
    PlayerCreateView,
    PlayerUpdateView,
    PlayerDeleteView,
    PlayerMatchesListView,
    )

"""
BASE ENDPOINT /players
"""
app_name = "players"

urlpatterns = [
    path("", PlayerListView.as_view(), name='player-list'),
    path("create/", PlayerCreateView.as_view(), name='player-create'),
    path("<slug:slug>/", PlayerDetailView.as_view(), name='player-detail'),
    path("<slug:slug>/update", PlayerUpdateView.as_view(), name='player-update'),
    path("<slug:slug>/delete", PlayerDeleteView.as_view(), name='player-delete'),
    path("<slug:slug>/matches", PlayerMatchesListView.as_view(), name='player-matches'),
]