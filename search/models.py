from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.utils.text import slugify
import json

class SearchIndex(models.Model):
    """
    A generic search index that can store any searchable content from any app.
    This makes the search future-proof as new apps and models can be easily added.
    """
    # Content type and object reference for generic relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Searchable content
    title = models.CharField(max_length=255)
    content = models.TextField()
    description = models.TextField(blank=True, null=True)
    
    # Metadata for better search results
    app_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    url = models.CharField(max_length=500, blank=True, null=True)
    
    # Additional searchable fields (stored as JSON)
    searchable_fields = models.JSONField(default=dict, blank=True)
    
    # User who created the content (if applicable)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search relevance and visibility
    is_public = models.BooleanField(default=True)
    search_weight = models.PositiveIntegerField(default=1, help_text='Higher weight = more relevant in search')
    
    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['content']),
            models.Index(fields=['app_name', 'model_name']),
            models.Index(fields=['is_public']),
            models.Index(fields=['search_weight']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = 'Search Indices'
    
    def __str__(self):
        return f"{self.title} ({self.app_name}.{self.model_name})"
    
    def get_absolute_url(self):
        """Get the URL for this search result"""
        if self.url:
            return self.url
        return f"/{self.app_name}/{self.object_id}/"
    
    def get_icon(self):
        """Get appropriate icon based on app and model"""
        icon_map = {
            'files': 'document',
            'images': 'photo',
            'prompts': 'light-bulb',
            'userprofile': 'user',
            'main': 'home',
        }
        return icon_map.get(self.app_name, 'document')
    
    def get_color(self):
        """Get appropriate color based on app"""
        color_map = {
            'files': 'blue',
            'images': 'green',
            'prompts': 'purple',
            'userprofile': 'orange',
            'main': 'gray',
        }
        return color_map.get(self.app_name, 'gray')

class SearchHistory(models.Model):
    """Track user search history for analytics and suggestions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=255)
    results_count = models.PositiveIntegerField(default=0)
    clicked_result = models.ForeignKey(SearchIndex, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = 'Search Histories'
    
    def __str__(self):
        return f"{self.query} by {self.user.username if self.user else 'Anonymous'}"

class SearchSuggestion(models.Model):
    """Popular search terms and suggestions"""
    term = models.CharField(max_length=255, unique=True)
    frequency = models.PositiveIntegerField(default=1)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['term']),
            models.Index(fields=['frequency']),
            models.Index(fields=['is_featured']),
        ]
        ordering = ['-frequency', '-last_searched']
    
    def __str__(self):
        return f"{self.term} ({self.frequency} searches)"