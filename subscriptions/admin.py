from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'amount', 'billing_cycle', 'is_api_enabled', 'next_due_date', 'is_active')
    list_filter = ('billing_cycle', 'is_active', 'is_api_enabled')
    search_fields = ('name', 'provider', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'provider', 'amount', 'billing_cycle')
        }),
        ('Dates', {
            'fields': ('start_date', 'next_due_date')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('API Configuration', {
            'fields': ('is_api_enabled', 'api_base_url', 'api_key', 'api_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
