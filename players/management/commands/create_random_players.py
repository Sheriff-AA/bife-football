import random
from faker import Faker
from django.core.management.base import BaseCommand
from players.models import Player, Team, User

class Command(BaseCommand):
    help = 'Creates random records for Player model'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Number of players to create')

    def handle(self, *args, **kwargs):
        fake = Faker()
        total = kwargs['total']

        positions = ["CB","LCB","RCB","RB","LB","CM","CAM","LAM","RAM","LWB","RWB","ST","LW","RW",]

        for _ in range(total):
            # Generate random user data
            username = fake.user_name()
            email = fake.email()
            password = fake.password()

            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_player=True  # Set the user as a player
                )


            first_name = fake.first_name()
            last_name = fake.last_name()
            shirt_number = random.randint(1, 99)
            age = random.randint(17, 40)
            position = random.choice(positions)

            # Create the player record
            player = Player.objects.create(
                first_name=first_name,
                last_name=last_name,
                shirt_number=shirt_number,
                age=age,
                position=position,
                user=user
            )

            # Add random teams (assuming you have existing teams)
            teams = Team.objects.order_by('?')[:random.randint(1, 2)]  # Add random 1-3 teams
            player.teams.add(*teams)

            self.stdout.write(self.style.SUCCESS(f'Player "{player}" created successfully.'))
