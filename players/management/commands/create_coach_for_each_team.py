import random
from faker import Faker
from django.core.management.base import BaseCommand
from players.models import Coach, Team, User

class Command(BaseCommand):
    help = 'Creates a coach for each team'

    def handle(self, *args, **kwargs):
        fake = Faker()

        teams = Team.objects.all()

        for team in teams:
            # Generate random user data
            username = fake.user_name()
            email = fake.email()
            password = fake.password()

            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_coach=True  # Set the user as a coach
            )

            first_name = fake.first_name()
            last_name = fake.last_name()

            # Create the coach record
            coach = Coach.objects.create(
                first_name=first_name,
                last_name=last_name,
                team=team,
                user=user
            )

            self.stdout.write(self.style.SUCCESS(f'Coach "{coach}" created successfully for team "{team}".'))