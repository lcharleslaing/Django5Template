from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from surveys.models import Survey, Section, Question


class Command(BaseCommand):
    help = 'Seed the "Balanced Honesty" template survey with sections and questions'

    def handle(self, *args, **options):
        # Get or create a superuser for the survey
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            user.set_password('admin')
            user.save()
            self.stdout.write(
                self.style.SUCCESS('Created admin user: admin/admin')
            )

        # Create the Balanced Honesty survey
        survey, created = Survey.objects.get_or_create(
            title='Balanced Honesty Survey',
            defaults={
                'description': 'A comprehensive survey designed to encourage honest feedback while maintaining appropriate levels of accountability and privacy.',
                'publish_start': timezone.now() + timedelta(days=1),
                'publish_end': timezone.now() + timedelta(days=30),
                'status': 'DRAFT',
                'created_by': user,
                'k_threshold': 5,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created survey: {survey.title}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Survey already exists: {survey.title}')
            )

        # Section 1: Trust & Safety (Escrow)
        section1, created = Section.objects.get_or_create(
            survey=survey,
            title='Trust & Safety',
            defaults={
                'description': 'Questions about workplace safety, trust, and reporting mechanisms',
                'order': 1,
            }
        )
        
        if created:
            self.stdout.write(f'Created section: {section1.title}')
            
            # Question 1.1: Overall Safety
            Question.objects.create(
                section=section1,
                type='LIKERT',
                prompt='How safe do you feel in your workplace?',
                help_text='1 = Not safe at all, 5 = Extremely safe',
                required=True,
                scale_min=1,
                scale_max=5,
                order=1,
                anonymity_mode='ESCROW'
            )
            
            # Question 1.2: Trust in Management
            Question.objects.create(
                section=section1,
                type='LIKERT',
                prompt='How much do you trust management to address safety concerns?',
                help_text='1 = No trust, 5 = Complete trust',
                required=True,
                scale_min=1,
                scale_max=5,
                order=2,
                anonymity_mode='ESCROW'
            )
            
            # Question 1.3: Safety Reporting
            Question.objects.create(
                section=section1,
                type='LONG_TEXT',
                prompt='Describe any safety concerns you have observed or experienced. What would help you feel more comfortable reporting them?',
                help_text='Be as specific as possible while maintaining your comfort level',
                required=False,
                order=3,
                anonymity_mode='ESCROW'
            )

        # Section 2: Workload & Clarity (Escrow)
        section2, created = Section.objects.get_or_create(
            survey=survey,
            title='Workload & Clarity',
            defaults={
                'description': 'Questions about workload management, role clarity, and work-life balance',
                'order': 2,
            }
        )
        
        if created:
            self.stdout.write(f'Created section: {section2.title}')
            
            # Question 2.1: Workload Assessment
            Question.objects.create(
                section=section2,
                type='LIKERT',
                prompt='How would you rate your current workload?',
                help_text='1 = Too light, 3 = Just right, 5 = Too heavy',
                required=True,
                scale_min=1,
                scale_max=5,
                order=1,
                anonymity_mode='ESCROW'
            )
            
            # Question 2.2: Role Clarity
            Question.objects.create(
                section=section2,
                type='LIKERT',
                prompt='How clear are you about your role and responsibilities?',
                help_text='1 = Very unclear, 5 = Crystal clear',
                required=True,
                scale_min=1,
                scale_max=5,
                order=2,
                anonymity_mode='ESCROW'
            )
            
            # Question 2.3: Work-Life Balance
            Question.objects.create(
                section=section2,
                type='LIKERT',
                prompt='How satisfied are you with your work-life balance?',
                help_text='1 = Very dissatisfied, 5 = Very satisfied',
                required=True,
                scale_min=1,
                scale_max=5,
                order=3,
                anonymity_mode='ESCROW'
            )
            
            # Question 2.4: Workload Suggestions
            Question.objects.create(
                section=section2,
                type='LONG_TEXT',
                prompt='What specific changes would help improve your workload or work-life balance?',
                help_text='Be specific about what would help you',
                required=False,
                order=4,
                anonymity_mode='ESCROW'
            )

        # Section 3: Commitments (Signed)
        section3, created = Section.objects.get_or_create(
            survey=survey,
            title='Commitments & Accountability',
            defaults={
                'description': 'Questions about commitments, goals, and accountability (signed responses)',
                'order': 3,
            }
        )
        
        if created:
            self.stdout.write(f'Created section: {section3.title}')
            
            # Question 3.1: Goal Commitment
            Question.objects.create(
                section=section3,
                type='LIKERT',
                prompt='How committed are you to achieving your team\'s goals this quarter?',
                help_text='1 = Not committed, 5 = Fully committed',
                required=True,
                scale_min=1,
                scale_max=5,
                order=1,
                anonymity_mode='SIGNED'
            )
            
            # Question 3.2: Personal Goals
            Question.objects.create(
                section=section3,
                type='LONG_TEXT',
                prompt='What are your top 3 professional goals for the next 6 months?',
                help_text='Be specific and realistic about what you want to achieve',
                required=True,
                order=2,
                anonymity_mode='SIGNED'
            )
            
            # Question 3.3: Support Needed
            Question.objects.create(
                section=section3,
                type='LONG_TEXT',
                prompt='What support or resources do you need to achieve these goals?',
                help_text='Be specific about what would help you succeed',
                required=False,
                order=3,
                anonymity_mode='SIGNED'
            )

        # Section 4: eNPS & Open Floor (Anonymous)
        section4, created = Section.objects.get_or_create(
            survey=survey,
            title='Overall Satisfaction & Feedback',
            defaults={
                'description': 'Net Promoter Score and open feedback (completely anonymous)',
                'order': 4,
            }
        )
        
        if created:
            self.stdout.write(f'Created section: {section4.title}')
            
            # Question 4.1: Net Promoter Score
            Question.objects.create(
                section=section4,
                type='NPS',
                prompt='How likely are you to recommend this organization as a place to work?',
                help_text='0 = Not at all likely, 10 = Extremely likely',
                required=True,
                scale_min=0,
                scale_max=10,
                order=1,
                anonymity_mode='ANONYMOUS'
            )
            
            # Question 4.2: Open Floor
            Question.objects.create(
                section=section4,
                type='LONG_TEXT',
                prompt='What else would you like to share? This is your opportunity to provide any additional feedback, suggestions, or concerns.',
                help_text='This is completely anonymous - share whatever is on your mind',
                required=False,
                order=2,
                anonymity_mode='ANONYMOUS'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded "Balanced Honesty" survey with {survey.sections.count()} sections and '
                f'{sum(section.questions.count() for section in survey.sections.all())} questions'
            )
        )
        
        # Display survey summary
        self.stdout.write('\nSurvey Summary:')
        self.stdout.write(f'Title: {survey.title}')
        self.stdout.write(f'Status: {survey.status}')
        self.stdout.write(f'URL: /admin/surveys/survey/{survey.pk}/change/')
        
        for section in survey.sections.all().order_by('order'):
            self.stdout.write(f'\n{section.title}:')
            for question in section.questions.all().order_by('order'):
                anonymity_badge = {
                    'ANONYMOUS': '🔒',
                    'ESCROW': '🔐', 
                    'SIGNED': '✍️'
                }.get(question.anonymity_mode, '❓')
                
                self.stdout.write(
                    f'  {anonymity_badge} {question.prompt[:60]}...'
                )
