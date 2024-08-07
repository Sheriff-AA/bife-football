"""
URL configuration for bifefootball project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from players.views import LandingPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name="landing-page"),
    path("matches/", include("matches.urls", namespace="matches")),
    path("admins/", include("admins.urls", namespace="admins")),
    path("players/", include("players.urls", namespace="players")),
    path("organizations/", include("organizations.urls", namespace="organizations")),
    path("teams/", include("teams.urls", namespace="teams")),
    path('accounts/', include('allauth.urls')),
    path("custommatches/", include("custommatches.urls", namespace="custommatches")),
]
