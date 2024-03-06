from django.urls import path
from .views import MatchListView, MatchDetailView

"""
BASE ENDPOINT /matches
"""
app_name = "matches"

urlpatterns = [
    path("", MatchListView.as_view(), name='match-list'),
    # path("create/", PlayerCreateView.as_view(), name='player-create'),
    path("<slug:slug>/", MatchDetailView.as_view(), name='match-detail'),
]