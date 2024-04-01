import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserExtraFields

class Command(BaseCommand):
    help = 'Imports user data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row['username']
                password = row['password'] 
                openai_api_key = row['openaiapi_key']
                prowritingaid_api_key = row['prowritingaidapi_key']
                salt = row['salt']
                admin = row['admin']
                subscribed = row['subscribed']
                subscription_id = row['subscription_id']
                usage = row['usage']

                # Convert empty strings to False for boolean fields
                admin = bool(admin) if admin else False
                subscribed = bool(subscribed) if subscribed else False

                # Replace empty usage with 0
                usage = int(usage) if usage else 0

                # Create a new User
                user = User.objects.create_user(username=username, password=password)
                user.is_staff = admin
                user.save()

                user_extra = UserExtraFields.objects.create(
                    user=user,
                    openai_api_key=openai_api_key,
                    prowritingaid_api_key=prowritingaid_api_key,
                    salt=salt,
                    subscribed=subscribed,
                    subscription_id=subscription_id,
                    usage=usage
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))
