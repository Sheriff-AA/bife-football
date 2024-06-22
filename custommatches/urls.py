from django.urls import path

from .views import CstmMatchCreateView, CstmMatchCreateEventView, CstmMatchDetailView, CstmResultCreateView, CstmMatchPlayerStatCreateEventView

"""
BASE ENDPOINT /custommatches
"""
app_name = "custommatches"

urlpatterns = [
    path("create/", CstmMatchCreateView.as_view(), name='custommatch-create'),
    path("create_custom_result/<slug:slug>", CstmResultCreateView.as_view(), name='custom-create-result'),
    path("create_custom_playerstat/<slug:slug>/", CstmMatchPlayerStatCreateEventView.as_view(), name='custom-playerstat-create'),
    path("create_custom_event/<slug:slug>/", CstmMatchCreateEventView.as_view(), name='custommatch-event-create'),
    path("<slug:slug>/", CstmMatchDetailView.as_view(), name='custommatch-detail'),
]