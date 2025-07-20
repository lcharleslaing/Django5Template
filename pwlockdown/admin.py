from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    PasswordCategory, PasswordEntry, PasswordShare, PasswordFolder,
    UserProfile, SecurityLog, PasswordGenerator, ImportExportLog
)


@admin.register(PasswordCategory)
class PasswordCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_display', 'icon', 'entry_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'
    
    def entry_count(self, obj):
        return obj.entries.count()
    entry_count.short_description = 'Entries'


@admin.register(PasswordEntry)
class PasswordEntryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'category', 'password_strength', 'is_favorite',
        'is_shared', 'expires_soon', 'last_used', 'created_at'
    ]
    list_filter = [
        'password_strength', 'is_favorite', 'is_shared', 'requires_2fa',
        'created_at', 'last_used', 'category', 'user'
    ]
    search_fields = ['title', 'username', 'email', 'website_url', 'user__username']
    readonly_fields = [
        'encrypted_password', 'password_strength', 'created_at', 'updated_at',
        'password_changed_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'username', 'email', 'website_url', 'category', 'user')
        }),
        ('Password & Security', {
            'fields': ('encrypted_password', 'password_strength', 'requires_2fa', 'password_changed_at')
        }),
        ('Organization', {
            'fields': ('notes', 'tags', 'custom_fields', 'is_favorite')
        }),
        ('Sharing', {
            'fields': ('is_shared',)
        }),
        ('Expiration', {
            'fields': ('expires_at', 'last_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def expires_soon(self, obj):
        if obj.expires_at:
            days = obj.days_until_expiry()
            if days is not None:
                if days <= 7:
                    return format_html('<span style="color: red;">⚠ {} days</span>', days)
                elif days <= 30:
                    return format_html('<span style="color: orange;">⚠ {} days</span>', days)
                else:
                    return f"{days} days"
        return "No expiry"
    expires_soon.short_description = 'Expires'


@admin.register(PasswordShare)
class PasswordShareAdmin(admin.ModelAdmin):
    list_display = [
        'password_entry', 'shared_by', 'shared_with', 'permission_level',
        'is_active', 'shared_at', 'expires_at'
    ]
    list_filter = ['permission_level', 'is_active', 'shared_at', 'expires_at']
    search_fields = [
        'password_entry__title', 'shared_by__username', 'shared_with__username'
    ]
    readonly_fields = ['shared_at']


@admin.register(PasswordFolder)
class PasswordFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'parent', 'full_path', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def full_path(self, obj):
        return obj.get_full_path()
    full_path.short_description = 'Full Path'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'two_factor_enabled', 'theme', 'session_timeout',
        'password_expiry_notifications', 'created_at'
    ]
    list_filter = [
        'two_factor_enabled', 'theme', 'auto_lock_enabled',
        'password_expiry_notifications', 'weak_password_alerts',
        'login_notifications', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['totp_secret', 'backup_codes', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Security Settings', {
            'fields': (
                'two_factor_enabled', 'totp_secret', 'backup_codes',
                'session_timeout', 'auto_lock_enabled'
            )
        }),
        ('Password Generation Preferences', {
            'fields': (
                'default_password_length', 'include_uppercase', 'include_lowercase',
                'include_numbers', 'include_symbols', 'exclude_ambiguous'
            )
        }),
        ('Notifications', {
            'fields': (
                'password_expiry_notifications', 'weak_password_alerts',
                'login_notifications'
            )
        }),
        ('UI Preferences', {
            'fields': ('theme', 'items_per_page')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'action', 'success', 'resource_type', 'ip_address',
        'timestamp'
    ]
    list_filter = [
        'action', 'success', 'resource_type', 'timestamp'
    ]
    search_fields = [
        'user__username', 'action', 'resource_type', 'ip_address'
    ]
    readonly_fields = [
        'user', 'action', 'resource_type', 'resource_id', 'details',
        'ip_address', 'user_agent', 'timestamp', 'success'
    ]
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Security logs should not be manually added
    
    def has_change_permission(self, request, obj=None):
        return False  # Security logs should not be edited


@admin.register(PasswordGenerator)
class PasswordGeneratorAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'length', 'character_types', 'exclude_ambiguous',
        'created_at'
    ]
    list_filter = [
        'include_uppercase', 'include_lowercase', 'include_numbers',
        'include_symbols', 'exclude_ambiguous', 'created_at'
    ]
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    def character_types(self, obj):
        types = []
        if obj.include_uppercase:
            types.append('ABC')
        if obj.include_lowercase:
            types.append('abc')
        if obj.include_numbers:
            types.append('123')
        if obj.include_symbols:
            types.append('!@#')
        return ' + '.join(types) if types else 'None'
    character_types.short_description = 'Character Types'


@admin.register(ImportExportLog)
class ImportExportLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'operation', 'format', 'file_name', 'records_processed',
        'success_rate', 'timestamp'
    ]
    list_filter = ['operation', 'format', 'success', 'timestamp']
    search_fields = ['user__username', 'file_name']
    readonly_fields = [
        'user', 'operation', 'format', 'file_name', 'records_processed',
        'records_successful', 'records_failed', 'error_details',
        'timestamp', 'success'
    ]
    date_hierarchy = 'timestamp'
    
    def success_rate(self, obj):
        if obj.records_processed > 0:
            rate = (obj.records_successful / obj.records_processed) * 100
            color = 'green' if rate >= 90 else 'orange' if rate >= 70 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color,
                rate
            )
        return "N/A"
    success_rate.short_description = 'Success Rate'
    
    def has_add_permission(self, request):
        return False  # Import/Export logs should not be manually added
    
    def has_change_permission(self, request, obj=None):
        return False  # Import/Export logs should not be edited


# Customize admin site header and title
admin.site.site_header = "PWLockdown Password Manager"
admin.site.site_title = "PWLockdown Admin"
admin.site.index_title = "Password Manager Administration"
