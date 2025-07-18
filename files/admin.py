from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'file_size', 'file_extension')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('title', 'description', 'uploaded_by__username')
    readonly_fields = ('uploaded_at', 'file_size')
    date_hierarchy = 'uploaded_at'
    
    def file_extension(self, obj):
        return obj.file_extension()
    file_extension.short_description = 'Type'
