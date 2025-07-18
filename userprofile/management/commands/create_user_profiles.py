from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from userprofile.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile objects for existing users who do not have profiles'

    def handle(self, *args, **options):
        users_without_profiles = []
        
        for user in User.objects.all():
            try:
                # Try to access the profile
                user.profile
            except UserProfile.DoesNotExist:
                users_without_profiles.append(user)
        
        if not users_without_profiles:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles!')
            )
            return
        
        self.stdout.write(
            f'Creating profiles for {len(users_without_profiles)} users...'
        )
        
        created_count = 0
        for user in users_without_profiles:
            try:
                UserProfile.objects.create(user=user)
                created_count += 1
                self.stdout.write(
                    f'Created profile for user: {user.username}'
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to create profile for {user.username}: {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} user profiles!'
            )
        ) 