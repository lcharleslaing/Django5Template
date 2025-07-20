from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.apps import apps
import random


class Command(BaseCommand):
    help = 'Populate sample data for testing dashboard and search functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating sample data...'))
        
        # Create some test users if they don't exist
        for i in range(3):
            username = f'testuser{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='testpass123'
                )
                self.stdout.write(f'Created user: {username}')
        
        # Get all users for data creation
        users = list(User.objects.all())
        
        # Populate data for each app
        self.populate_prompts_data(users)
        self.populate_userprofiles_data(users)
        
        self.stdout.write(self.style.SUCCESS('Sample data population completed!'))
    
    def populate_prompts_data(self, users):
        """Populate prompts app data"""
        try:
            Category = apps.get_model('prompts', 'Category')
            Tag = apps.get_model('prompts', 'Tag')
            Prompt = apps.get_model('prompts', 'Prompt')
            
            # Create categories
            categories_data = [
                {'name': 'Code Generation', 'description': 'Prompts for generating code', 'color': '#10B981'},
                {'name': 'Writing', 'description': 'Creative writing prompts', 'color': '#8B5CF6'},
                {'name': 'Analysis', 'description': 'Data analysis prompts', 'color': '#F59E0B'},
            ]
            
            categories = []
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    defaults=cat_data
                )
                categories.append(category)
                if created:
                    self.stdout.write(f'Created category: {category.name}')
            
            # Create tags
            tags_data = [
                {'name': 'Python', 'color': '#3776AB'},
                {'name': 'JavaScript', 'color': '#F7DF1E'},
                {'name': 'Creative', 'color': '#FF6B6B'},
                {'name': 'Business', 'color': '#4ECDC4'},
            ]
            
            tags = []
            for tag_data in tags_data:
                tag, created = Tag.objects.get_or_create(
                    name=tag_data['name'],
                    defaults=tag_data
                )
                tags.append(tag)
                if created:
                    self.stdout.write(f'Created tag: {tag.name}')
            
            # Create prompts
            prompts_data = [
                {
                    'title': 'Python Function Generator',
                    'description': 'Generate Python functions based on requirements',
                    'content': 'Create a Python function that {requirement} with proper error handling and documentation.',
                    'prompt_type': 'code',
                    'difficulty': 'intermediate',
                },
                {
                    'title': 'Creative Story Starter',
                    'description': 'Generate creative story beginnings',
                    'content': 'Write the opening paragraph of a story about {theme} that captures the reader\'s attention.',
                    'prompt_type': 'creative',
                    'difficulty': 'beginner',
                },
                {
                    'title': 'Data Analysis Report',
                    'description': 'Analyze data and provide insights',
                    'content': 'Analyze the following data: {data}. Provide key insights, trends, and actionable recommendations.',
                    'prompt_type': 'analysis',
                    'difficulty': 'advanced',
                },
            ]
            
            for prompt_data in prompts_data:
                if not Prompt.objects.filter(title=prompt_data['title']).exists():
                    prompt = Prompt.objects.create(
                        **prompt_data,
                        category=random.choice(categories),
                        author=random.choice(users)
                    )
                    prompt.tags.set(random.sample(tags, 2))
                    self.stdout.write(f'Created prompt: {prompt.title}')
                    
        except Exception as e:
            self.stdout.write(f'Error populating prompts data: {e}')
    
    def populate_userprofiles_data(self, users):
        """Populate user profiles data"""
        try:
            UserProfile = apps.get_model('userprofile', 'UserProfile')
            
            profiles_data = [
                {
                    'bio': 'Full-stack developer with expertise in Python and JavaScript',
                    'company': 'Tech Innovations Inc',
                    'position': 'Senior Developer',
                    'location': 'San Francisco, CA',
                },
                {
                    'bio': 'UI/UX designer passionate about creating beautiful user experiences',
                    'company': 'Design Studio LLC',
                    'position': 'Lead Designer',
                    'location': 'New York, NY',
                },
                {
                    'bio': 'Data scientist specializing in machine learning and analytics',
                    'company': 'Data Corp',
                    'position': 'Data Scientist',
                    'location': 'Austin, TX',
                },
            ]
            
            for i, profile_data in enumerate(profiles_data):
                if i < len(users):
                    user = users[i]
                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults=profile_data
                    )
                    if created:
                        self.stdout.write(f'Created profile for: {user.username}')
                    
        except Exception as e:
            self.stdout.write(f'Error populating user profiles data: {e}')