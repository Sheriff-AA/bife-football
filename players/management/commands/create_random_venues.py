import random
from faker import Faker
from faker import Factory
from django.core.management.base import BaseCommand
from players.models import Venue

class Command(BaseCommand):
    help = 'Creates random records for Venue model'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Number of venues to create')

    def handle(self, *args, **kwargs):
        fake = Factory.create('en_IE')
        total = kwargs['total']

        for _ in range(total):
            name = fake.city()

            # Create the venue record
            venue = Venue.objects.create(
                name=name
            )

            self.stdout.write(self.style.SUCCESS(f'Venue "{venue}" created successfully.'))
