from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
import random

class Command(BaseCommand):
    help = 'Create sample data for testing the dashboard'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username to create data for')

    def handle(self, *args, **options):
        username = options['user'] or 'testuser'

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User {username} does not exist. Please create the user first.')
            )
            return

        self.stdout.write(f'Creating sample data for user: {username}')

        # Create sample prompts
        try:
            from prompts.models import Prompt, Category, Tag

            # Create categories if they don't exist
            categories = [
                Category.objects.get_or_create(name='AI & Machine Learning')[0],
                Category.objects.get_or_create(name='Web Development')[0],
                Category.objects.get_or_create(name='Creative Writing')[0],
            ]

            # Create tags if they don't exist
            tags = [
                Tag.objects.get_or_create(name='Python')[0],
                Tag.objects.get_or_create(name='JavaScript')[0],
                Tag.objects.get_or_create(name='AI')[0],
                Tag.objects.get_or_create(name='Creative')[0],
            ]

            prompt_titles = [
                'Python Web Scraping Script',
                'AI Chatbot Response Generator',
                'JavaScript Form Validation',
                'Creative Story Generator',
                'Data Analysis Pipeline',
                'API Integration Helper',
                'CSS Animation Effects',
                'Database Query Optimizer',
            ]

            for i, title in enumerate(prompt_titles):
                prompt = Prompt.objects.create(
                    title=title,
                    content=f'This is a sample prompt for {title}. It contains detailed instructions and examples.',
                    author=user,
                    category=random.choice(categories),
                    is_public=True,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                prompt.tags.add(random.choice(tags))

            self.stdout.write(f'Created {len(prompt_titles)} sample prompts')

        except ImportError:
            self.stdout.write('Prompts app not available, skipping...')

        # Create sample subscriptions
        try:
            from subscriptions.models import Subscription

            subscription_data = [
                {'name': 'OpenAI API Subscription', 'amount': 20.00, 'billing_cycle': 'monthly'},
                {'name': 'GitHub Pro', 'amount': 4.00, 'billing_cycle': 'monthly'},
                {'name': 'Notion Premium', 'amount': 8.00, 'billing_cycle': 'monthly'},
                {'name': 'Spotify Premium', 'amount': 9.99, 'billing_cycle': 'monthly'},
            ]

            today = date.today()

            for data in subscription_data:
                start_date = today - timedelta(days=random.randint(0, 60))
                next_due_date = start_date + timedelta(days=30)  # Monthly billing

                Subscription.objects.create(
                    name=data['name'],
                    amount=data['amount'],
                    billing_cycle=data['billing_cycle'],
                    start_date=start_date,
                    next_due_date=next_due_date,
                    user=user,
                    is_active=True,
                    is_api_enabled=random.choice([True, False]),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 60))
                )

            self.stdout.write(f'Created {len(subscription_data)} sample subscriptions')

        except ImportError:
            self.stdout.write('Subscriptions app not available, skipping...')

        # Create sample files
        try:
            from files.models import File
            from django.core.files.base import ContentFile

            file_names = [
                'project_documentation.pdf',
                'presentation_slides.pptx',
                'code_review_notes.txt',
                'meeting_minutes.docx',
                'design_mockups.sketch',
            ]

            for file_name in file_names:
                # Create a simple text file content
                content = f"This is a sample {file_name} content for testing purposes."
                file_obj = File(
                    title=file_name.replace('_', ' ').replace('.', ' ').title(),
                    uploaded_by=user,
                )
                file_obj.file.save(file_name, ContentFile(content.encode()), save=False)
                file_obj.uploaded_at = timezone.now() - timedelta(days=random.randint(0, 45))
                file_obj.save()

            self.stdout.write(f'Created {len(file_names)} sample files')

        except ImportError:
            self.stdout.write('Files app not available, skipping...')

        # Create sample images
        try:
            from images.models import Image
            from django.core.files.base import ContentFile
            from PIL import Image as PILImage
            import io

            image_names = [
                'screenshot_2024_01_15.png',
                'profile_photo.jpg',
                'banner_image.png',
                'logo_design.svg',
                'mockup_preview.jpg',
            ]

            for image_name in image_names:
                # Create a simple 100x100 colored image
                img = PILImage.new('RGB', (100, 100), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

                # Save to bytes
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)

                image_obj = Image(
                    title=image_name.replace('_', ' ').replace('.', ' ').title(),
                    uploaded_by=user,
                )
                image_obj.image.save(image_name, ContentFile(buffer.getvalue()), save=False)
                image_obj.uploaded_at = timezone.now() - timedelta(days=random.randint(0, 30))
                image_obj.save()

            self.stdout.write(f'Created {len(image_names)} sample images')

        except ImportError:
            self.stdout.write('Images app not available, skipping...')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample dashboard data!')
        )