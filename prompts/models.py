from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text='Hex color code (e.g., #3B82F6)')
    icon = models.CharField(max_length=50, default='light-bulb', help_text='Heroicon name (e.g., light-bulb, code, cog)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('prompts:category_detail', kwargs={'pk': self.pk})

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6B7280', help_text='Hex color code (e.g., #6B7280)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('prompts:tag_detail', kwargs={'pk': self.pk})

class Prompt(models.Model):
    PROMPT_TYPES = [
        ('text', 'Text Prompt'),
        ('code', 'Code Prompt'),
        ('creative', 'Creative Writing'),
        ('analysis', 'Analysis'),
        ('instruction', 'Instruction'),
        ('question', 'Question'),
        ('template', 'Template'),
    ]

    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(help_text='Brief description of what this prompt does')
    content = models.TextField(help_text='The actual prompt text')

    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='prompts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='prompts')
    prompt_type = models.CharField(max_length=20, choices=PROMPT_TYPES, default='text')
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_LEVELS, default='intermediate')

    # Usage and Performance
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text='Success rate percentage')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    # Examples and Context
    example_input = models.TextField(blank=True, null=True, help_text='Example input for the prompt')
    example_output = models.TextField(blank=True, null=True, help_text='Example output from the prompt')
    context_notes = models.TextField(blank=True, null=True, help_text='Additional context or instructions')

    # Metadata
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_prompts')
    is_public = models.BooleanField(default=True, help_text='Whether this prompt is visible to all users')
    is_featured = models.BooleanField(default=False, help_text='Featured prompts appear prominently')
    is_template = models.BooleanField(default=False, help_text='Template prompts can be used as starting points')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['prompt_type']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1

            while Prompt.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('prompts:prompt_detail', kwargs={'slug': self.slug})

    def increment_usage(self):
        """Increment the usage count"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    def update_rating(self, new_rating):
        """Update the average rating"""
        # This is a simplified version - in a real app you'd want a separate Rating model
        if self.average_rating == 0:
            self.average_rating = new_rating
        else:
            # Simple average - in production you'd want to track individual ratings
            self.average_rating = (self.average_rating + new_rating) / 2
        self.save(update_fields=['average_rating'])

    @property
    def short_description(self):
        """Return a shortened version of the description"""
        if len(self.description) <= 150:
            return self.description
        return self.description[:147] + '...'

    @property
    def difficulty_color(self):
        """Return color based on difficulty level"""
        colors = {
            'beginner': 'success',
            'intermediate': 'warning',
            'advanced': 'error',
            'expert': 'secondary',
        }
        return colors.get(self.difficulty, 'neutral')

class PromptUsage(models.Model):
    """Track individual prompt usage for analytics"""
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompt_usages')
    input_text = models.TextField(blank=True, null=True)
    output_text = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True, null=True)
    execution_time = models.DurationField(blank=True, null=True)
    tokens_used = models.PositiveIntegerField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['prompt', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} used {self.prompt.title} on {self.created_at.date()}"

class PromptCollection(models.Model):
    """Collections of prompts for organization"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    prompts = models.ManyToManyField(Prompt, related_name='collections')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompt_collections')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('prompts:collection_detail', kwargs={'pk': self.pk})
