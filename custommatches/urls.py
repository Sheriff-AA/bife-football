from django.urls import path

from .views import CustomMatchCreateView, CustomMatchCreateEventView, CustomMatchDetailView, CustomResultCreateView, CustomMatchPlayerStatCreateEventView

"""
BASE ENDPOINT /custommatches
"""
app_name = "custommatches"

urlpatterns = [
    path("create/", CustomMatchCreateView.as_view(), name='custommatch-create'),
    path("custom-result/<slug:slug>", CustomResultCreateView.as_view(), name='custom-create-result'),
    path("custom-playerstat/<slug:slug>/", CustomMatchPlayerStatCreateEventView.as_view(), name='custom-playerstat-create'),
    path("custom-event/<slug:slug>/", CustomMatchCreateEventView.as_view(), name='custommatch-event-create'),
    path("<slug:slug>/", CustomMatchDetailView.as_view(), name='custommatch-detail'),
]