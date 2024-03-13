from django.urls import path
from .views import MatchListView, MatchDetailView, MatchCreateView

"""
BASE ENDPOINT /matches
"""
app_name = "matches"

urlpatterns = [
    path("", MatchListView.as_view(), name='match-list'),
    path("create/", MatchCreateView.as_view(), name='match-create'),
    path("<slug:slug>/", MatchDetailView.as_view(), name='match-detail'),
]