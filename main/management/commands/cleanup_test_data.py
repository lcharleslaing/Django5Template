from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from prompts.models import Prompt
from subscriptions.models import Subscription
from files.models import File
from images.models import Image

class Command(BaseCommand):
    help = 'Clean up test data created by sample data commands'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='testuser',
            help='Username of the test user whose data should be cleaned up'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        username = options['user']
        dry_run = options['dry_run']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found.'))
            return

        self.stdout.write(f'Cleaning up data for user: {username}')

        # Count items to be deleted
        prompt_count = Prompt.objects.filter(author=user).count()
        subscription_count = Subscription.objects.filter(user=user).count()
        file_count = File.objects.filter(uploaded_by=user).count()
        image_count = Image.objects.filter(uploaded_by=user).count()

        total_count = prompt_count + subscription_count + file_count + image_count

        if total_count == 0:
            self.stdout.write(self.style.WARNING('No test data found for this user.'))
            return

        self.stdout.write(f'Found {total_count} items to clean up:')
        self.stdout.write(f'  - Prompts: {prompt_count}')
        self.stdout.write(f'  - Subscriptions: {subscription_count}')
        self.stdout.write(f'  - Files: {file_count}')
        self.stdout.write(f'  - Images: {image_count}')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No data will be deleted.'))
            return

        # Confirm deletion
        confirm = input(f'Are you sure you want to delete all data for user "{username}"? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('Operation cancelled.')
            return

        # Delete the data
        deleted_prompts = Prompt.objects.filter(author=user).delete()
        deleted_subscriptions = Subscription.objects.filter(user=user).delete()
        deleted_files = File.objects.filter(uploaded_by=user).delete()
        deleted_images = Image.objects.filter(uploaded_by=user).delete()

        self.stdout.write(self.style.SUCCESS('Cleanup completed successfully!'))
        self.stdout.write(f'Deleted:')
        self.stdout.write(f'  - {deleted_prompts[0]} prompts')
        self.stdout.write(f'  - {deleted_subscriptions[0]} subscriptions')
        self.stdout.write(f'  - {deleted_files[0]} files')
        self.stdout.write(f'  - {deleted_images[0]} images')