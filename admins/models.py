from django.db import models

from players.models import User, Team


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='admin')
