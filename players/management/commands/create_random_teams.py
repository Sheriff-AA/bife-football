import random
from faker import Faker
from django.core.management.base import BaseCommand
from players.models import Team, User

class Command(BaseCommand):
    help = 'Creates random records for Team model'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Number of teams to create')

    def handle(self, *args, **kwargs):
        fake = Faker()
        total = kwargs['total']

        # Create 10 random users
        random_users = []
        for _ in range(10):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            random_users.append(user)

        for _ in range(total):
            team_name = fake.company()
            short_team_name = ''.join(fake.words(nb=1, unique=True)).upper()[:3]  # Random 3-character string
            organisation = random.choice(random_users)

            # Create the team record
            team = Team.objects.create(
                team_name=team_name,
                short_team_name=short_team_name,
                organisation=organisation
            )

            self.stdout.write(self.style.SUCCESS(f'Team "{team}" created successfully.'))
