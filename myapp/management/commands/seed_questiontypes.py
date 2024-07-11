from django.core.management.base import BaseCommand
from myapp.models import QuestionType  # Replace 'app_name' with the name of your Django app

class Command(BaseCommand):
    help = 'Seeds the database with QuestionType data'

    def handle(self, *args, **kwargs):
        # Define the seed data
        question_types = [
            {'id': 1, 'name': 'multiple choice'},
            {'id': 2, 'name': 'true false'},
            {'id': 3, 'name': 'short answer'},
        ]

        # Iterate over the seed data and create records
        for qt in question_types:
            QuestionType.objects.update_or_create(
                id=qt['id'],
                defaults={'name': qt['name']},
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded QuestionType data'))