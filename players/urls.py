from django.urls import path
from .views import PlayerListView, PlayerDetailView, PlayerCreateView

"""
BASE ENDPOINT /players
"""
app_name = "players"

urlpatterns = [
    path("", PlayerListView.as_view(), name='player-list'),
    path("create/", PlayerCreateView.as_view(), name='player-create'),
    path("<slug:slug>/", PlayerDetailView.as_view(), name='player-detail'),
]