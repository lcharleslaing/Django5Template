from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SubscriptionPlan, AppDefinition, AppPermission, 
    UserSubscription, GroupAppPermission, AppVisibilityOverride
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'max_users', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['price', 'name']


@admin.register(AppDefinition)
class AppDefinitionAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'url_name', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['order', 'display_name']
    list_editable = ['is_active', 'order']


@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ['plan', 'app', 'can_access', 'can_create', 'can_edit', 'can_delete', 'can_export', 'can_import']
    list_filter = ['plan', 'app', 'can_access', 'can_create', 'can_edit', 'can_delete']
    search_fields = ['plan__name', 'app__display_name']
    ordering = ['plan', 'app__order']
    list_editable = ['can_access', 'can_create', 'can_edit', 'can_delete', 'can_export', 'can_import']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'is_active', 'starts_at', 'expires_at', 'is_expired_display']
    list_filter = ['plan', 'is_active', 'starts_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'plan__name']
    ordering = ['-created_at']
    list_editable = ['is_active']

    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_display.short_description = 'Status'


@admin.register(GroupAppPermission)
class GroupAppPermissionAdmin(admin.ModelAdmin):
    list_display = ['group', 'app', 'can_access', 'can_create', 'can_edit', 'can_delete', 'can_export', 'can_import']
    list_filter = ['group', 'app', 'can_access', 'can_create', 'can_edit', 'can_delete']
    search_fields = ['group__name', 'app__display_name']
    ordering = ['group', 'app__order']
    list_editable = ['can_access', 'can_create', 'can_edit', 'can_delete', 'can_export', 'can_import']


@admin.register(AppVisibilityOverride)
class AppVisibilityOverrideAdmin(admin.ModelAdmin):
    list_display = ['user', 'app', 'is_visible', 'can_access', 'can_create', 'can_edit', 'can_delete', 'can_export', 'can_import', 'reason', 'created_at']
    list_filter = ['is_visible', 'can_access', 'can_create', 'can_edit', 'created_at']
    search_fields = ['user__username', 'app__display_name', 'reason']
    ordering = ['user', 'app__order']
    list_editable = ['is_visible', 'can_access', 'can_create', 'can_edit', 'can_delete', 'can_export', 'can_import']