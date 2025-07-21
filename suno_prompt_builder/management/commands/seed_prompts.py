from django.core.management.base import BaseCommand
from suno_prompt_builder.models import SongPrompt


class Command(BaseCommand):
    help = 'Seed the database with example song prompts'

    def handle(self, *args, **options):
        # Clear existing prompts
        SongPrompt.objects.all().delete()
        
        # Create example prompts
        prompts_data = [
            {
                'title': 'Midnight Disco Dreams',
                'lyrics': 'Dancing through the neon lights, feeling the rhythm of the night',
                'subject': 'A disco song about dancing in the city at night',
                'styles': ['disco', 'funk', 'electronic'],
                'excluded_styles': ['heavy metal', 'country'],
                'weirdness': 30,
                'style_influence': 80,
                'is_instrumental': False
            },
            {
                'title': 'Cinematic Adventure',
                'subject': 'An epic orchestral piece for a fantasy movie scene',
                'lyrics': '',
                'styles': ['cinematic', 'orchestral', 'epic'],
                'excluded_styles': ['pop', 'rap'],
                'weirdness': 20,
                'style_influence': 90,
                'is_instrumental': True
            },
            {
                'title': 'Cyberpunk Streets',
                'lyrics': 'Neon lights reflect in the rain, as we walk through digital pain',
                'subject': 'A cyberpunk rap song about urban life in the future',
                'styles': ['rap', 'electronic', 'cyberpunk'],
                'excluded_styles': ['folk', 'jazz'],
                'weirdness': 70,
                'style_influence': 60,
                'is_instrumental': False
            }
        ]
        
        for prompt_data in prompts_data:
            SongPrompt.objects.create(**prompt_data)
            self.stdout.write(
                self.style.SUCCESS(f'Created prompt: {prompt_data["title"]}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(prompts_data)} example prompts')
        )