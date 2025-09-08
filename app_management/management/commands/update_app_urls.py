from django.core.management.base import BaseCommand
from app_management.models import AppDefinition


class Command(BaseCommand):
    help = 'Update app URL names to correct values'

    def handle(self, *args, **options):
        self.stdout.write('Updating app URL names...')
        
        # URL name corrections
        url_corrections = {
            'prompts': 'prompts:prompt_list',
            'subscriptions': 'subscriptions:subscription_list',
            'files': 'files:file_list',
            'images': 'images:image_list',
            'surveys': 'surveys:index',
            'equipment_bom': 'equipment_bom:dashboard',
            'suno_prompt_builder': 'suno_prompt_builder:prompt_builder',
        }
        
        for app_name, correct_url in url_corrections.items():
            try:
                app = AppDefinition.objects.get(name=app_name)
                app.url_name = correct_url
                app.save()
                self.stdout.write(f'Updated {app.display_name}: {correct_url}')
            except AppDefinition.DoesNotExist:
                self.stdout.write(f'App {app_name} not found')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated app URL names!')
        )
