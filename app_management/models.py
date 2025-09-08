from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator


class SubscriptionPlan(models.Model):
    """Subscription plans that control app access"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    max_users = models.PositiveIntegerField(default=1, help_text="Maximum number of users for this plan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price', 'name']

    def __str__(self):
        return f"{self.name} (${self.price})"


class AppDefinition(models.Model):
    """Definition of available apps in the system"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    url_name = models.CharField(max_length=100, help_text="URL name for the app (e.g., 'prompts:index')")
    icon_class = models.CharField(max_length=100, blank=True, help_text="CSS class for the icon")
    icon_svg = models.TextField(blank=True, help_text="SVG path for the icon")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order in navigation")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'display_name']

    def __str__(self):
        return self.display_name


class AppPermission(models.Model):
    """Permissions for apps based on subscription plans"""
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='app_permissions')
    app = models.ForeignKey(AppDefinition, on_delete=models.CASCADE, related_name='permissions')
    can_access = models.BooleanField(default=True)
    can_create = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_import = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['plan', 'app']
        ordering = ['plan', 'app__order']

    def __str__(self):
        return f"{self.plan.name} - {self.app.display_name}"


class UserSubscription(models.Model):
    """User subscription assignments"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='app_subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='users')
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class GroupAppPermission(models.Model):
    """App permissions for Django groups"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='app_permissions')
    app = models.ForeignKey(AppDefinition, on_delete=models.CASCADE, related_name='group_permissions')
    can_access = models.BooleanField(default=True)
    can_create = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_import = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group', 'app']
        ordering = ['group', 'app__order']

    def __str__(self):
        return f"{self.group.name} - {self.app.display_name}"


class AppVisibilityOverride(models.Model):
    """Override app visibility for specific users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_overrides')
    app = models.ForeignKey(AppDefinition, on_delete=models.CASCADE, related_name='user_overrides')
    is_visible = models.BooleanField(default=True)
    can_access = models.BooleanField(default=True)
    can_create = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_import = models.BooleanField(default=False)
    reason = models.CharField(max_length=200, blank=True, help_text="Reason for this override")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_overrides')

    class Meta:
        unique_together = ['user', 'app']
        ordering = ['user', 'app__order']

    def __str__(self):
        return f"{self.user.username} - {self.app.display_name} ({'Visible' if self.is_visible else 'Hidden'})"