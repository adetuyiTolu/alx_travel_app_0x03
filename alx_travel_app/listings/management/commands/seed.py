from django.core.management.base import BaseCommand
from listings.models import Listing
from django.contrib.auth import get_user_model
from faker import Faker
import random

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding listings...")

        host, _ = User.objects.get_or_create(
                email='host@example.com',
                password='password123',
                first_name='Host',
                last_name='User',
            )
        self.stdout.write("Created sample host user.")
            
        for _ in range(10):
            Listing.objects.create(
                host=host,
                name=fake.company(),
                description=fake.text(max_nb_chars=200),
                location=fake.city(),
                price_per_night=random.uniform(50, 500)
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded listings.'))
