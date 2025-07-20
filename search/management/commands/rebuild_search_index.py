from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from search.models import SearchIndex


class Command(BaseCommand):
    help = 'Rebuild the search index from all apps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Rebuild index for a specific app only',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing index before rebuilding',
        )

    def handle(self, *args, **options):
        app_name = options.get('app')
        clear_index = options.get('clear')

        if clear_index:
            self.stdout.write('Clearing existing search index...')
            SearchIndex.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Search index cleared.'))

        if app_name:
            self.stdout.write(f'Rebuilding search index for app: {app_name}')
            self.rebuild_app_index(app_name)
        else:
            self.stdout.write('Rebuilding search index for all apps...')
            self.rebuild_all_indexes()

        self.stdout.write(self.style.SUCCESS('Search index rebuild completed!'))

    def rebuild_all_indexes(self):
        """Rebuild search index for all apps"""
        indexed_count = 0

        for app_config in apps.get_app_configs():
            app_name = app_config.label

            # Skip Django's built-in apps and our search app
            if app_name in ['admin', 'auth', 'contenttypes', 'sessions', 'search']:
                continue

            self.stdout.write(f'Processing app: {app_name}')
            app_count = self.rebuild_app_index(app_name)
            indexed_count += app_count

        self.stdout.write(f'Total items indexed: {indexed_count}')

    def rebuild_app_index(self, app_name):
        """Rebuild search index for a specific app"""
        indexed_count = 0

        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            self.stdout.write(self.style.ERROR(f'App "{app_name}" not found.'))
            return 0

        for model in app_config.get_models():
            model_name = model.__name__
            self.stdout.write(f'  Processing model: {model_name}')

            # Check if model has searchable fields
            if hasattr(model, 'get_search_content'):
                # Use custom search method
                for obj in model.objects.all():
                    try:
                        search_data = obj.get_search_content()
                        SearchIndex.objects.update_or_create(
                            content_type=ContentType.objects.get_for_model(model),
                            object_id=obj.id,
                            defaults={
                                'title': search_data.get('title', str(obj)),
                                'content': search_data.get('content', ''),
                                'description': search_data.get('description', ''),
                                'app_name': app_name,
                                'model_name': model_name,
                                'url': search_data.get('url', ''),
                                'created_by': getattr(obj, 'created_by', None) or getattr(obj, 'uploaded_by', None) or getattr(obj, 'author', None),
                                'search_weight': search_data.get('weight', 1),
                                'is_public': search_data.get('is_public', True),
                                'searchable_fields': search_data.get('fields', {})
                            }
                        )
                        indexed_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error indexing {app_name}.{model_name} {obj.id}: {e}'))
            else:
                # Default indexing for common fields
                searchable_fields = ['title', 'name', 'description', 'content']
                available_fields = [f.name for f in model._meta.fields if f.name in searchable_fields]

                if available_fields:
                    for obj in model.objects.all():
                        try:
                            title = getattr(obj, 'title', None) or getattr(obj, 'name', None) or str(obj)
                            content = ' '.join([
                                str(getattr(obj, field, ''))
                                for field in available_fields
                                if getattr(obj, field, None)
                            ])

                            if title and content:
                                SearchIndex.objects.update_or_create(
                                    content_type=ContentType.objects.get_for_model(model),
                                    object_id=obj.id,
                                    defaults={
                                        'title': title,
                                        'content': content,
                                        'description': getattr(obj, 'description', ''),
                                        'app_name': app_name,
                                        'model_name': model_name,
                                        'created_by': getattr(obj, 'created_by', None) or getattr(obj, 'uploaded_by', None) or getattr(obj, 'author', None),
                                        'is_public': True
                                    }
                                )
                                indexed_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Error indexing {app_name}.{model_name} {obj.id}: {e}'))

        self.stdout.write(f'  Indexed {indexed_count} items from {app_name}')
        return indexed_count