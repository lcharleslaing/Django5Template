from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from app_management.models import (
    SubscriptionPlan, AppDefinition, AppPermission, 
    GroupAppPermission, UserSubscription
)


class Command(BaseCommand):
    help = 'Set up initial app visibility system with default plans and app definitions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up app visibility system...')
        
        # Create default subscription plans
        plans = self.create_subscription_plans()
        
        # Create app definitions
        apps = self.create_app_definitions()
        
        # Create default groups
        groups = self.create_default_groups()
        
        # Set up permissions
        self.setup_permissions(plans, apps, groups)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up app visibility system!')
        )

    def create_subscription_plans(self):
        """Create default subscription plans"""
        plans_data = [
            {
                'name': 'Free',
                'description': 'Basic access to core features',
                'price': 0.00,
                'max_users': 1,
            },
            {
                'name': 'Basic',
                'description': 'Standard access to most features',
                'price': 9.99,
                'max_users': 5,
            },
            {
                'name': 'Professional',
                'description': 'Full access to all features',
                'price': 29.99,
                'max_users': 25,
            },
            {
                'name': 'Enterprise',
                'description': 'Unlimited access with advanced features',
                'price': 99.99,
                'max_users': 1000,
            },
        ]
        
        plans = {}
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            plans[plan_data['name']] = plan
            if created:
                self.stdout.write(f'Created plan: {plan.name}')
            else:
                self.stdout.write(f'Plan already exists: {plan.name}')
        
        return plans

    def create_app_definitions(self):
        """Create app definitions for all available apps"""
        apps_data = [
            {
                'name': 'prompts',
                'display_name': 'AI Prompts',
                'description': 'Create and manage AI prompts',
                'url_name': 'prompts:prompt_list',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
                'order': 1,
            },
            {
                'name': 'subscriptions',
                'display_name': 'Subscriptions',
                'description': 'Manage subscription plans and billing',
                'url_name': 'subscriptions:subscription_list',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
                'order': 2,
            },
            {
                'name': 'files',
                'display_name': 'Files',
                'description': 'Upload and manage files',
                'url_name': 'files:file_list',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
                'order': 3,
            },
            {
                'name': 'images',
                'display_name': 'Images',
                'description': 'Upload and manage images',
                'url_name': 'images:image_list',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
                'order': 4,
            },
            {
                'name': 'surveys',
                'display_name': 'Surveys',
                'description': 'Create and manage surveys',
                'url_name': 'surveys:index',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
                'order': 5,
            },
            {
                'name': 'equipment_bom',
                'display_name': 'Equipment BOM',
                'description': 'Manage equipment bills of materials',
                'url_name': 'equipment_bom:dashboard',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
                'order': 6,
            },
            {
                'name': 'suno_prompt_builder',
                'display_name': 'Suno Prompt Builder',
                'description': 'Build prompts for Suno AI music generation',
                'url_name': 'suno_prompt_builder:prompt_builder',
                'icon_class': 'w-4 h-4',
                'icon_svg': 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3',
                'order': 7,
            },
        ]
        
        apps = {}
        for app_data in apps_data:
            app, created = AppDefinition.objects.get_or_create(
                name=app_data['name'],
                defaults=app_data
            )
            apps[app_data['name']] = app
            if created:
                self.stdout.write(f'Created app: {app.display_name}')
            else:
                self.stdout.write(f'App already exists: {app.display_name}')
        
        return apps

    def create_default_groups(self):
        """Create default user groups"""
        groups_data = [
            {
                'name': 'Free Users',
                'description': 'Users with free subscription',
            },
            {
                'name': 'Basic Users',
                'description': 'Users with basic subscription',
            },
            {
                'name': 'Professional Users',
                'description': 'Users with professional subscription',
            },
            {
                'name': 'Enterprise Users',
                'description': 'Users with enterprise subscription',
            },
            {
                'name': 'Administrators',
                'description': 'System administrators',
            },
        ]
        
        groups = {}
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name']
            )
            groups[group_data['name']] = group
            if created:
                self.stdout.write(f'Created group: {group.name}')
            else:
                self.stdout.write(f'Group already exists: {group.name}')
        
        return groups

    def setup_permissions(self, plans, apps, groups):
        """Set up default permissions for plans and groups"""
        
        # Free plan permissions (limited access)
        free_plan = plans['Free']
        free_apps = ['prompts', 'files', 'images']
        for app_name in free_apps:
            if app_name in apps:
                AppPermission.objects.get_or_create(
                    plan=free_plan,
                    app=apps[app_name],
                    defaults={
                        'can_access': True,
                        'can_create': True,
                        'can_edit': True,
                        'can_delete': False,
                        'can_export': False,
                        'can_import': False,
                    }
                )
        
        # Basic plan permissions (more access)
        basic_plan = plans['Basic']
        basic_apps = ['prompts', 'subscriptions', 'files', 'images', 'surveys']
        for app_name in basic_apps:
            if app_name in apps:
                AppPermission.objects.get_or_create(
                    plan=basic_plan,
                    app=apps[app_name],
                    defaults={
                        'can_access': True,
                        'can_create': True,
                        'can_edit': True,
                        'can_delete': True,
                        'can_export': True,
                        'can_import': False,
                    }
                )
        
        # Professional plan permissions (most access)
        pro_plan = plans['Professional']
        pro_apps = ['prompts', 'subscriptions', 'files', 'images', 'surveys', 'equipment_bom', 'suno_prompt_builder']
        for app_name in pro_apps:
            if app_name in apps:
                AppPermission.objects.get_or_create(
                    plan=pro_plan,
                    app=apps[app_name],
                    defaults={
                        'can_access': True,
                        'can_create': True,
                        'can_edit': True,
                        'can_delete': True,
                        'can_export': True,
                        'can_import': True,
                    }
                )
        
        # Enterprise plan permissions (all access)
        enterprise_plan = plans['Enterprise']
        for app_name, app in apps.items():
            AppPermission.objects.get_or_create(
                plan=enterprise_plan,
                app=app,
                defaults={
                    'can_access': True,
                    'can_create': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_export': True,
                    'can_import': True,
                }
            )
        
        # Group permissions (similar to plans)
        group_permissions = {
            'Free Users': free_apps,
            'Basic Users': basic_apps,
            'Professional Users': pro_apps,
            'Enterprise Users': list(apps.keys()),
            'Administrators': list(apps.keys()),
        }
        
        for group_name, app_names in group_permissions.items():
            if group_name in groups:
                group = groups[group_name]
                for app_name in app_names:
                    if app_name in apps:
                        GroupAppPermission.objects.get_or_create(
                            group=group,
                            app=apps[app_name],
                            defaults={
                                'can_access': True,
                                'can_create': True,
                                'can_edit': True,
                                'can_delete': group_name in ['Administrators', 'Enterprise Users'],
                                'can_export': group_name in ['Basic Users', 'Professional Users', 'Enterprise Users', 'Administrators'],
                                'can_import': group_name in ['Professional Users', 'Enterprise Users', 'Administrators'],
                            }
                        )
        
        self.stdout.write('Set up permissions for all plans and groups')
