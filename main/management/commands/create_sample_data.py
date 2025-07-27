from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random

from prompts.models import Category, Tag, Prompt
from files.models import File
from images.models import Image
from subscriptions.models import Subscription
from userprofile.models import UserProfile

class Command(BaseCommand):
    help = 'Create sample data for testing search functionality'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create a test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')

        # Create categories (public, so no user filter needed)
        categories = []
        category_names = ['AI & Machine Learning', 'Web Development', 'Creative Writing', 'Data Analysis', 'Productivity']
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Sample category for {name}',
                    'color': f'#{random.randint(0, 0xFFFFFF):06x}',
                    'icon': 'light-bulb'
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {name}')

        # Create tags (public, so no user filter needed)
        tags = []
        tag_names = ['python', 'javascript', 'ai', 'productivity', 'tutorial', 'advanced', 'beginner']
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={
                    'color': f'#{random.randint(0, 0xFFFFFF):06x}'
                }
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {name}')

        # Create prompts for the test user
        prompt_data = [
            {
                'title': 'Python Web Scraping Script',
                'description': 'A comprehensive web scraping script using Python and BeautifulSoup',
                'content': 'Create a web scraper that extracts data from websites...',
                'category': categories[1],  # Web Development
                'tags': [tags[0], tags[4]],  # python, tutorial
                'difficulty': 'intermediate'
            },
            {
                'title': 'AI Chatbot Implementation',
                'description': 'Build a simple chatbot using natural language processing',
                'content': 'Implement a chatbot that can understand and respond to user queries...',
                'category': categories[0],  # AI & Machine Learning
                'tags': [tags[2], tags[0]],  # ai, python
                'difficulty': 'advanced'
            },
            {
                'title': 'Creative Story Generator',
                'description': 'Generate creative stories using AI prompts',
                'content': 'Create a story generator that produces engaging narratives...',
                'category': categories[2],  # Creative Writing
                'tags': [tags[2], tags[3]],  # ai, productivity
                'difficulty': 'beginner'
            },
            {
                'title': 'Data Visualization Dashboard',
                'description': 'Build an interactive dashboard for data visualization',
                'content': 'Create a dashboard that displays data in various chart formats...',
                'category': categories[3],  # Data Analysis
                'tags': [tags[0], tags[1]],  # python, javascript
                'difficulty': 'intermediate'
            },
            {
                'title': 'Productivity Task Manager',
                'description': 'A simple task management system for personal productivity',
                'content': 'Build a task manager that helps organize daily activities...',
                'category': categories[4],  # Productivity
                'tags': [tags[3], tags[5]],  # productivity, advanced
                'difficulty': 'intermediate'
            }
        ]

        for data in prompt_data:
            prompt, created = Prompt.objects.get_or_create(
                title=data['title'],
                author=user,  # Ensure it's created for the test user
                defaults={
                    'description': data['description'],
                    'content': data['content'],
                    'category': data['category'],
                    'difficulty': data['difficulty'],
                    'is_public': True
                }
            )
            if created:
                prompt.tags.set(data['tags'])
                self.stdout.write(f'Created prompt: {data["title"]}')

        # Create subscriptions for the test user
        subscription_data = [
            {
                'name': 'OpenAI API Plan',
                'provider': 'OpenAI',
                'amount': 29.99,
                'billing_cycle': 'monthly',
                'is_api_enabled': True,
                'api_base_url': 'https://api.openai.com/v1'
            },
            {
                'name': 'GitHub Pro',
                'provider': 'GitHub',
                'amount': 4.99,
                'billing_cycle': 'monthly',
                'is_api_enabled': False
            },
            {
                'name': 'Notion Premium',
                'provider': 'Notion',
                'amount': 8.00,
                'billing_cycle': 'monthly',
                'is_api_enabled': True,
                'api_base_url': 'https://api.notion.com/v1'
            }
        ]

        for data in subscription_data:
            subscription, created = Subscription.objects.get_or_create(
                name=data['name'],
                user=user,  # Ensure it's created for the test user
                defaults={
                    'provider': data['provider'],
                    'amount': data['amount'],
                    'billing_cycle': data['billing_cycle'],
                    'start_date': date.today() - timedelta(days=30),
                    'next_due_date': date.today() + timedelta(days=5),
                    'is_active': True,
                    'is_api_enabled': data['is_api_enabled'],
                    'api_base_url': data.get('api_base_url', ''),
                    'notes': f'Sample subscription for {data["name"]}'
                }
            )
            if created:
                self.stdout.write(f'Created subscription: {data["name"]}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Test user: {user.username} (password: testpass123)')
        self.stdout.write('All data is now user-scoped and will only appear for the test user.')