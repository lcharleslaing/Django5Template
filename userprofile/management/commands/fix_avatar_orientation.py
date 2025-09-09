from django.core.management.base import BaseCommand
from userprofile.models import UserProfile

class Command(BaseCommand):
    help = 'Fix orientation of all user avatars'

    def handle(self, *args, **options):
        profiles = UserProfile.objects.filter(avatar__isnull=False).exclude(avatar='')
        
        self.stdout.write(f'Found {profiles.count()} profiles with avatars')
        
        for profile in profiles:
            if profile.avatar and profile.avatar.name != 'avatars/default.png':
                try:
                    self.stdout.write(f'Processing avatar for {profile.user.username}...')
                    profile.resize_avatar()
                    self.stdout.write(self.style.SUCCESS(f'✓ Fixed avatar for {profile.user.username}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ Error processing avatar for {profile.user.username}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Avatar orientation fix completed!'))
