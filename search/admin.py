from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import SearchIndex, SearchHistory, SearchSuggestion


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ['title', 'app_name', 'model_name', 'created_by', 'search_weight', 'created_at', 'get_absolute_url_link']
    list_filter = ['app_name', 'model_name', 'is_public', 'search_weight', 'created_at']
    search_fields = ['title', 'content', 'description']
    readonly_fields = ['content_type', 'object_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_absolute_url_link(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">View</a>', obj.url)
        return format_html('<a href="{}" target="_blank">View</a>', obj.get_absolute_url())
    get_absolute_url_link.short_description = 'URL'
    
    def has_add_permission(self, request):
        return False  # SearchIndex should only be created programmatically


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'clicked_result', 'created_at']
    list_filter = ['created_at', 'results_count']
    search_fields = ['query', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # SearchHistory should only be created programmatically
    
    def has_change_permission(self, request, obj=None):
        return False  # SearchHistory should not be edited


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ['term', 'frequency', 'is_featured', 'created_at', 'last_searched']
    list_filter = ['is_featured', 'created_at', 'last_searched']
    search_fields = ['term']
    ordering = ['-frequency', '-last_searched']
    actions = ['mark_as_featured', 'unmark_as_featured']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} suggestions marked as featured.')
    mark_as_featured.short_description = "Mark selected suggestions as featured"
    
    def unmark_as_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} suggestions unmarked as featured.')
    unmark_as_featured.short_description = "Unmark selected suggestions as featured"


# Custom admin site configuration
admin.site.site_header = "Site Administration"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the Admin Portal"