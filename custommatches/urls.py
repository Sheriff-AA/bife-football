from django.urls import path

from .views import CstmMatchCreateView, CstmMatchCreateEventView, CstmMatchDetailView, CstmResultCreateView, CstmMatchPlayerStatCreateEventView

"""
BASE ENDPOINT /custommatches
"""
app_name = "custommatches"

urlpatterns = [
    path("create/", CstmMatchCreateView.as_view(), name='custommatch-create'),
    path("custom-result/<slug:slug>", CstmResultCreateView.as_view(), name='custom-create-result'),
    path("custom-playerstat/<slug:slug>/", CstmMatchPlayerStatCreateEventView.as_view(), name='custom-playerstat-create'),
    path("custom-event/<slug:slug>/", CstmMatchCreateEventView.as_view(), name='custommatch-event-create'),
    path("<slug:slug>/", CstmMatchDetailView.as_view(), name='custommatch-detail'),
]