from django.urls import path
from .views import MatchListView, MatchDetailView, MatchCreateView, MatchCreateEventView

"""
BASE ENDPOINT /matches
"""
app_name = "matches"

urlpatterns = [
    path("", MatchListView.as_view(), name='match-list'),
    path("create/", MatchCreateView.as_view(), name='match-create'),
    path("<slug:slug>/create-event/", MatchCreateEventView.as_view(), name='match-event-create'),
    path("<slug:slug>/", MatchDetailView.as_view(), name='match-detail'),
]