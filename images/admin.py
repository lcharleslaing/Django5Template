from django.contrib import admin
from .models import Image

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'file_size', 'width', 'height')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('title', 'description', 'uploaded_by__username')
    readonly_fields = ('uploaded_at', 'file_size', 'width', 'height', 'thumbnail')
    date_hierarchy = 'uploaded_at'
