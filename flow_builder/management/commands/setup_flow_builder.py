from django.core.management.base import BaseCommand
from flow_builder.models import Department, Person, Flow, Step, Task
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Set up sample data for Flow Builder'

    def handle(self, *args, **options):
        self.stdout.write('Setting up Flow Builder sample data...')
        
        # Create departments
        engineering, created = Department.objects.get_or_create(
            name='Engineering',
            defaults={'description': 'Software development and engineering'}
        )
        if created:
            self.stdout.write(f'Created department: {engineering.name}')
        
        marketing, created = Department.objects.get_or_create(
            name='Marketing',
            defaults={'description': 'Marketing and communications'}
        )
        if created:
            self.stdout.write(f'Created department: {marketing.name}')
        
        # Create people
        john, created = Person.objects.get_or_create(
            name='John Smith',
            defaults={'department': engineering}
        )
        if created:
            self.stdout.write(f'Created person: {john.name}')
        
        sarah, created = Person.objects.get_or_create(
            name='Sarah Johnson',
            defaults={'department': marketing}
        )
        if created:
            self.stdout.write(f'Created person: {sarah.name}')
        
        # Create a sample flow
        flow, created = Flow.objects.get_or_create(
            name='Website Redesign Project',
            defaults={
                'description': 'Complete redesign of the company website with new features and improved UX',
                'start_date': date.today()
            }
        )
        
        if created:
            self.stdout.write(f'Created flow: {flow.name}')
        
        # Create steps (whether flow was created or already existed)
        if not flow.steps.exists():
            self.stdout.write('Creating steps for flow...')
            
            # Create steps
            step1, created = Step.objects.get_or_create(
                flow=flow,
                title='Requirements Gathering',
                defaults={
                    'description': 'Collect and document all requirements from stakeholders',
                    'responsible_person': john,
                    'time_allotted_days': 5
                }
            )
            if created:
                self.stdout.write(f'Created step: {step1.title}')
            
            step2, created = Step.objects.get_or_create(
                flow=flow,
                title='Design Mockups',
                defaults={
                    'description': 'Create wireframes and visual mockups for the new design',
                    'responsible_person': sarah,
                    'time_allotted_days': 7
                }
            )
            if created:
                self.stdout.write(f'Created step: {step2.title}')
                # Add dependency
                step2.dependencies.add(step1)
            
            step3, created = Step.objects.get_or_create(
                flow=flow,
                title='Frontend Development',
                defaults={
                    'description': 'Implement the frontend based on approved designs',
                    'responsible_person': john,
                    'time_allotted_days': 10
                }
            )
            if created:
                self.stdout.write(f'Created step: {step3.title}')
                # Add dependency
                step3.dependencies.add(step2)
            
            step4, created = Step.objects.get_or_create(
                flow=flow,
                title='Testing & QA',
                defaults={
                    'description': 'Test all functionality and fix bugs',
                    'responsible_person': john,
                    'time_allotted_days': 3
                }
            )
            if created:
                self.stdout.write(f'Created step: {step4.title}')
                # Add dependency
                step4.dependencies.add(step3)
            
            step5, created = Step.objects.get_or_create(
                flow=flow,
                title='Deployment',
                defaults={
                    'description': 'Deploy to production and monitor for issues',
                    'responsible_person': john,
                    'time_allotted_days': 2
                }
            )
            if created:
                self.stdout.write(f'Created step: {step5.title}')
                # Add dependency
                step5.dependencies.add(step4)
            
            # Create some tasks
            Task.objects.get_or_create(
                step=step1,
                title='Interview stakeholders',
                defaults={
                    'description': 'Conduct interviews with key stakeholders',
                    'due_date': date.today() + timedelta(days=2)
                }
            )
            
            Task.objects.get_or_create(
                step=step1,
                title='Document requirements',
                defaults={
                    'description': 'Create detailed requirements document',
                    'due_date': date.today() + timedelta(days=4)
                }
            )
            
            Task.objects.get_or_create(
                step=step2,
                title='Create wireframes',
                defaults={
                    'description': 'Design low-fidelity wireframes',
                    'due_date': date.today() + timedelta(days=7)
                }
            )
            
            # Recalculate dates
            flow.recalculate_dates()
            self.stdout.write('Recalculated flow dates')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up Flow Builder sample data!')
        )
