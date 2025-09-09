from django.core.management.base import BaseCommand
from flow_builder.models import Step


class Command(BaseCommand):
    help = 'Update progress percentage for all steps based on their tasks'

    def handle(self, *args, **options):
        steps = Step.objects.all()
        updated_count = 0
        
        for step in steps:
            old_progress = step.progress_percentage
            step.update_progress()
            
            if step.progress_percentage != old_progress:
                step.save(update_fields=['progress_percentage', 'is_completed', 'actual_end_date'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated step "{step.title}": {old_progress}% -> {step.progress_percentage}%'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} steps')
        )
