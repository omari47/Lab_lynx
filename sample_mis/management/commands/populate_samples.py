# sample_mis/management/commands/populate_samples.py
from django.core.management.base import BaseCommand
from faker import Faker
from sample_mis.models import Sample
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate the database with fake sample data'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of samples to create')

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs['count']

        # Sample type and status choices
        SAMPLE_TYPES = ['Food', 'Chemical', 'Textile', 'Other']
        STATUS_CHOICES = ['Pending', 'In Progress', 'Completed']

        for _ in range(count):
            # Generate fake data
            batch_number = fake.bothify(text='BATCH-####')
            sample_type = random.choice(SAMPLE_TYPES)
            origin = fake.city()
            status = random.choice(STATUS_CHOICES)
            test_date = fake.date_between(start_date='-30d', end_date='now')
            metadata = fake.sentence(nb_words=10)

            # Create and save the sample
            Sample.objects.create(
                batch_number=batch_number,
                sample_type=sample_type,
                origin=origin,
                status=status,
                test_date=test_date,
                metadata=metadata
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} fake samples'))