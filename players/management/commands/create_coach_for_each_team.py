import random
from faker import Faker
from django.core.management.base import BaseCommand
from players.models import Coach, Team

class Command(BaseCommand):
    help = 'Creates a coach for each team'

    def handle(self, *args, **kwargs):
        fake = Faker()

        teams = Team.objects.all()

        for team in teams:
            first_name = fake.first_name()
            last_name = fake.last_name()

            # Create the coach record
            coach = Coach.objects.create(
                first_name=first_name,
                last_name=last_name,
                team=team
            )

            self.stdout.write(self.style.SUCCESS(f'Coach "{coach}" created successfully for team "{team}".'))