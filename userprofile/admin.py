from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'company', 'position', 'location', 'created_at')
    list_filter = ('created_at', 'company', 'location')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'company', 'position')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
