from django.urls import path
from .views import PlayerListView, PlayerDetailView

"""
BASE ENDPOINT /players
"""
app_name = "players"

urlpatterns = [
    path("", PlayerListView.as_view())
]