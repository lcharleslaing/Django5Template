from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app_management.models import SubscriptionPlan, UserSubscription


class Command(BaseCommand):
    help = 'Assign a subscription plan to a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to assign subscription to')
        parser.add_argument('plan_name', type=str, help='Name of the subscription plan')

    def handle(self, *args, **options):
        username = options['username']
        plan_name = options['plan_name']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist.')
            )
            return

        try:
            plan = SubscriptionPlan.objects.get(name=plan_name)
        except SubscriptionPlan.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Plan "{plan_name}" does not exist.')
            )
            return

        # Create or update user subscription
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={'plan': plan}
        )

        if not created:
            subscription.plan = plan
            subscription.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully assigned {plan.name} plan to {user.username}'
            )
        )
