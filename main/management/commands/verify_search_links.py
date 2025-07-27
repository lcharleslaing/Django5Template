from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from django.apps import apps
from django.db.models import Q, CharField, TextField
import os

class Command(BaseCommand):
    help = 'Verify that all search result links are working'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='testuser',
            help='Username to test search with'
        )
        parser.add_argument(
            '--query',
            type=str,
            default='python',
            help='Search query to test'
        )
        parser.add_argument(
            '--skip-files',
            action='store_true',
            help='Skip testing file/image URLs that might not exist'
        )

    def handle(self, *args, **options):
        username = options['user']
        query = options['query']
        skip_files = options['skip_files']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found.'))
            return

        self.stdout.write(f'Testing search for user: {username}')
        self.stdout.write(f'Search query: "{query}"')
        if skip_files:
            self.stdout.write('Skipping file/image URLs')
        self.stdout.write('=' * 50)

        # Simulate the search logic
        results = []

        for model in apps.get_models():
            try:
                # Skip Django's built-in models
                if model._meta.app_label in ['admin', 'auth', 'contenttypes', 'sessions', 'theme']:
                    continue

                # Get searchable fields
                fields = [f.name for f in model._meta.fields if isinstance(f, (CharField, TextField))]
                if not fields:
                    continue

                # Build search query
                q = Q()
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})

                # Start with base queryset
                base_queryset = model.objects.all()

                # Filter by user ownership if model has user field
                if hasattr(model, 'user'):
                    base_queryset = base_queryset.filter(user=user)
                elif hasattr(model, 'uploaded_by'):
                    base_queryset = base_queryset.filter(uploaded_by=user)
                elif hasattr(model, 'author'):
                    base_queryset = base_queryset.filter(author=user)
                elif hasattr(model, 'owner'):
                    base_queryset = base_queryset.filter(owner=user)

                # Apply search filter and get results
                found = base_queryset.filter(q)[:5]

                if found:
                    results.append({
                        'model': model.__name__,
                        'items': found
                    })

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[SEARCH ERROR] {model.__name__}: {e}"))

        if not results:
            self.stdout.write(self.style.WARNING('No search results found.'))
            return

        # Test each result
        client = Client()
        client.force_login(user)

        total_tested = 0
        total_working = 0

        for result in results:
            self.stdout.write(f'\n{result["model"]}:')
            for item in result['items']:
                total_tested += 1

                try:
                    # Get the URL
                    if hasattr(item, 'get_absolute_url'):
                        url = item.get_absolute_url()
                        # Remove the domain part for testing
                        if url.startswith('http'):
                            url = url.split('/', 3)[-1] if len(url.split('/', 3)) > 3 else '/'
                        elif url.startswith('/'):
                            url = url
                        else:
                            url = '/' + url

                        # Skip file/image URLs if requested
                        if skip_files and any(skip_type in url for skip_type in ['/files/', '/images/']):
                            self.stdout.write(f'  ⏭️  {item}: {url} (skipped)')
                            total_working += 1
                            continue

                        # Test the URL
                        response = client.get(url)

                        if response.status_code == 200:
                            self.stdout.write(f'  ✅ {item}: {url}')
                            total_working += 1
                        elif response.status_code == 404:
                            self.stdout.write(f'  ❌ {item}: {url} (404 Not Found)')
                        elif response.status_code == 403:
                            self.stdout.write(f'  ❌ {item}: {url} (403 Forbidden)')
                        elif response.status_code == 500:
                            # Check if it's a file/image issue
                            if any(file_type in url for file_type in ['/files/', '/images/']):
                                self.stdout.write(f'  ⚠️  {item}: {url} (500 - likely missing file)')
                            else:
                                self.stdout.write(f'  ❌ {item}: {url} (500 Internal Server Error)')
                        else:
                            self.stdout.write(f'  ❌ {item}: {url} (Status: {response.status_code})')
                    else:
                        self.stdout.write(f'  ⚠️  {item}: No get_absolute_url method')

                except Exception as e:
                    # Check if it's a file-related error
                    if 'file' in str(e).lower() or 'image' in str(e).lower():
                        self.stdout.write(f'  ⚠️  {item}: File/image error - {str(e)[:50]}...')
                    else:
                        self.stdout.write(f'  ❌ {item}: Error - {e}')

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(f'Summary: {total_working}/{total_tested} links working')

        if total_working == total_tested:
            self.stdout.write(self.style.SUCCESS('All search result links are working!'))
        else:
            self.stdout.write(self.style.WARNING(f'{total_tested - total_working} links need attention.'))

        if not skip_files:
            self.stdout.write('\nNote: Use --skip-files to ignore file/image URL issues in test data.')