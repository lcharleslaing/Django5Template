from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models import Q
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Test the search functionality across all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='test',
            help='Search query to test'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )

    def handle(self, *args, **options):
        query = options['query']
        verbose = options['verbose']
        
        self.stdout.write(self.style.SUCCESS(f'Testing search functionality with query: "{query}"'))
        self.stdout.write('')
        
        total_results = 0
        
        # Search across all models dynamically
        for model in apps.get_models():
            if hasattr(model, '_meta'):
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                
                # Skip Django's built-in models
                if app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                    continue
                
                try:
                    # Build search query dynamically
                    search_fields = []
                    
                    # Get all text fields for searching
                    for field in model._meta.fields:
                        if field.get_internal_type() in ['CharField', 'TextField']:
                            search_fields.append(field.name)
                    
                    if search_fields:
                        # Build Q object for OR search across all text fields
                        q_objects = Q()
                        for field in search_fields:
                            q_objects |= Q(**{f'{field}__icontains': query})
                        
                        # Execute search
                        matches = model.objects.filter(q_objects)
                        count = matches.count()
                        total_results += count
                        
                        if count > 0 or verbose:
                            self.stdout.write(f'{app_label}.{model_name}: {count} results')
                            
                            if verbose and count > 0:
                                for match in matches[:3]:  # Show first 3 results
                                    self.stdout.write(f'  - {str(match)}')
                                if count > 3:
                                    self.stdout.write(f'  ... and {count - 3} more')
                                self.stdout.write('')
                    
                    elif verbose:
                        self.stdout.write(f'{app_label}.{model_name}: No searchable fields')
                
                except Exception as e:
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f'{app_label}.{model_name}: Error - {str(e)}')
                        )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'Search test completed. Total results: {total_results}')
        )
        
        # Test API endpoint functionality
        self.stdout.write('')
        self.stdout.write('Testing search fields discovery:')
        
        for model in apps.get_models():
            if hasattr(model, '_meta'):
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                
                # Skip Django's built-in models
                if app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                    continue
                
                try:
                    search_fields = []
                    for field in model._meta.fields:
                        if field.get_internal_type() in ['CharField', 'TextField']:
                            search_fields.append(field.name)
                    
                    if search_fields:
                        self.stdout.write(f'{app_label}.{model_name}: {", ".join(search_fields)}')
                
                except Exception:
                    continue