from django.contrib import admin
from .models import Prompt, Category, Tag, PromptUsage, PromptCollection

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'prompt_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def prompt_count(self, obj):
        return obj.prompts.count()
    prompt_count.short_description = 'Prompts'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'prompt_count', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    def prompt_count(self, obj):
        return obj.prompts.count()
    prompt_count.short_description = 'Prompts'

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'prompt_type', 'difficulty', 
        'is_public', 'is_featured', 'usage_count', 'average_rating', 'created_at'
    ]
    list_filter = [
        'prompt_type', 'difficulty', 'is_public', 'is_featured', 'is_template',
        'category', 'tags', 'created_at'
    ]
    search_fields = ['title', 'description', 'content', 'author__username']
    readonly_fields = ['slug', 'usage_count', 'success_rate', 'average_rating', 'created_at', 'updated_at', 'last_used']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'content', 'author')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'prompt_type', 'difficulty')
        }),
        ('Examples & Context', {
            'fields': ('example_input', 'example_output', 'context_notes'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_public', 'is_featured', 'is_template')
        }),
        ('Statistics', {
            'fields': ('usage_count', 'success_rate', 'average_rating', 'last_used'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PromptUsage)
class PromptUsageAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'user', 'rating', 'tokens_used', 'cost', 'created_at']
    list_filter = ['rating', 'created_at', 'prompt__category']
    search_fields = ['prompt__title', 'user__username', 'input_text', 'output_text']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('prompt', 'user', 'input_text', 'output_text')
        }),
        ('Feedback', {
            'fields': ('rating', 'feedback')
        }),
        ('Analytics', {
            'fields': ('execution_time', 'tokens_used', 'cost'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(PromptCollection)
class PromptCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'prompt_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['prompts']
    
    def prompt_count(self, obj):
        return obj.prompts.count()
    prompt_count.short_description = 'Prompts'
