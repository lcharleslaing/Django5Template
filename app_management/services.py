from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import (
    AppDefinition, AppPermission, UserSubscription, 
    GroupAppPermission, AppVisibilityOverride
)


class AppVisibilityService:
    """Service class to determine app visibility and permissions for users"""
    
    def __init__(self, user):
        self.user = user
        self._user_subscription = None
        self._user_groups = None
    
    @property
    def user_subscription(self):
        """Get user's subscription plan"""
        if self._user_subscription is None:
            try:
                self._user_subscription = self.user.app_subscription
            except UserSubscription.DoesNotExist:
                self._user_subscription = None
        return self._user_subscription
    
    @property
    def user_groups(self):
        """Get user's groups"""
        if self._user_groups is None:
            self._user_groups = self.user.groups.all()
        return self._user_groups
    
    def get_visible_apps(self):
        """Get list of apps visible to the user"""
        visible_apps = []
        
        # Get all active apps
        apps = AppDefinition.objects.filter(is_active=True).order_by('order', 'display_name')
        
        for app in apps:
            if self.can_access_app(app):
                visible_apps.append({
                    'app': app,
                    'permissions': self.get_app_permissions(app)
                })
        
        return visible_apps
    
    def can_access_app(self, app):
        """Check if user can access a specific app"""
        # Check for user-specific override first
        try:
            override = AppVisibilityOverride.objects.get(user=self.user, app=app)
            return override.is_visible and override.can_access
        except AppVisibilityOverride.DoesNotExist:
            pass
        
        # Check subscription-based permissions
        if self.user_subscription and self.user_subscription.is_active and not self.user_subscription.is_expired:
            try:
                permission = AppPermission.objects.get(
                    plan=self.user_subscription.plan,
                    app=app
                )
                return permission.can_access
            except AppPermission.DoesNotExist:
                pass
        
        # Check group-based permissions
        for group in self.user_groups:
            try:
                permission = GroupAppPermission.objects.get(
                    group=group,
                    app=app
                )
                if permission.can_access:
                    return True
            except GroupAppPermission.DoesNotExist:
                continue
        
        # Default: superusers can access everything
        if self.user.is_superuser:
            return True
        
        # Default: staff users can access everything if no restrictions
        if self.user.is_staff:
            return True
        
        # Default: deny access
        return False
    
    def get_app_permissions(self, app):
        """Get detailed permissions for a specific app"""
        permissions = {
            'can_access': False,
            'can_create': False,
            'can_edit': False,
            'can_delete': False,
            'can_export': False,
            'can_import': False,
        }
        
        # Check for user-specific override first
        try:
            override = AppVisibilityOverride.objects.get(user=self.user, app=app)
            if override.is_visible:
                permissions.update({
                    'can_access': override.can_access,
                    'can_create': override.can_create,
                    'can_edit': override.can_edit,
                    'can_delete': override.can_delete,
                    'can_export': override.can_export,
                    'can_import': override.can_import,
                })
                return permissions
        except AppVisibilityOverride.DoesNotExist:
            pass
        
        # Check subscription-based permissions
        if self.user_subscription and self.user_subscription.is_active and not self.user_subscription.is_expired:
            try:
                permission = AppPermission.objects.get(
                    plan=self.user_subscription.plan,
                    app=app
                )
                permissions.update({
                    'can_access': permission.can_access,
                    'can_create': permission.can_create,
                    'can_edit': permission.can_edit,
                    'can_delete': permission.can_delete,
                    'can_export': permission.can_export,
                    'can_import': permission.can_import,
                })
                return permissions
            except AppPermission.DoesNotExist:
                pass
        
        # Check group-based permissions
        for group in self.user_groups:
            try:
                permission = GroupAppPermission.objects.get(
                    group=group,
                    app=app
                )
                if permission.can_access:
                    permissions.update({
                        'can_access': permission.can_access,
                        'can_create': permission.can_create,
                        'can_edit': permission.can_edit,
                        'can_delete': permission.can_delete,
                        'can_export': permission.can_export,
                        'can_import': permission.can_import,
                    })
                    return permissions
            except GroupAppPermission.DoesNotExist:
                continue
        
        # Default: superusers have all permissions
        if self.user.is_superuser:
            return {key: True for key in permissions.keys()}
        
        # Default: staff users have basic permissions if no restrictions
        if self.user.is_staff:
            return {
                'can_access': True,
                'can_create': True,
                'can_edit': True,
                'can_delete': False,
                'can_export': False,
                'can_import': False,
            }
        
        return permissions
    
    def get_user_subscription_info(self):
        """Get user's subscription information"""
        if not self.user_subscription:
            return None
        
        return {
            'plan': self.user_subscription.plan,
            'is_active': self.user_subscription.is_active,
            'is_expired': self.user_subscription.is_expired,
            'expires_at': self.user_subscription.expires_at,
        }
    
    def can_user_access_app(self, app_name):
        """Check if user can access an app by name"""
        try:
            app = AppDefinition.objects.get(name=app_name, is_active=True)
            return self.can_access_app(app)
        except AppDefinition.DoesNotExist:
            return False
    
    def get_app_permissions_by_name(self, app_name):
        """Get permissions for an app by name"""
        try:
            app = AppDefinition.objects.get(name=app_name, is_active=True)
            return self.get_app_permissions(app)
        except AppDefinition.DoesNotExist:
            return {
                'can_access': False,
                'can_create': False,
                'can_edit': False,
                'can_delete': False,
                'can_export': False,
                'can_import': False,
            }
