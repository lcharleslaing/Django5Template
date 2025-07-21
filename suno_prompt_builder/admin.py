from django.contrib import admin
from .models import SongPrompt


@admin.register(SongPrompt)
class SongPromptAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'weirdness', 'style_influence', 'is_instrumental', 'created_at']
    list_filter = ['is_instrumental', 'created_at', 'updated_at']
    search_fields = ['title', 'subject', 'lyrics']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subject', 'lyrics')
        }),
        ('Style Configuration', {
            'fields': ('styles', 'excluded_styles', 'weirdness', 'style_influence')
        }),
        ('Options', {
            'fields': ('is_instrumental',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')