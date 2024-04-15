from django.urls import path
from .views import (
    TeamListView,
    TeamCreateView,
    TeamDetailView,
    TeamDashboardView
    )

"""
BASE ENDPOINT /teams
"""
app_name = "teams"

urlpatterns = [
    path("", TeamListView.as_view(), name='team-list'),
    path("create/", TeamCreateView.as_view(), name='team-create'),
    path("<int:pk>/team-dashboard/", TeamDashboardView.as_view(), name='team-dashboard'),
    # path("confirm-result/<slug:slug>/", ResultCreateView.as_view(), name='result-create'),
    path("<int:pk>/", TeamDetailView.as_view(), name='team-detail'),
]