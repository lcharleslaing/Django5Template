from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image as PILImage
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png')
    bio = models.TextField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar if it exists and is not the default
        if self.avatar and self.avatar.name != 'avatars/default.png':
            self.resize_avatar()
    
    def resize_avatar(self):
        """Resize avatar to 300x300 pixels"""
        if self.avatar:
            try:
                with PILImage.open(self.avatar.path) as img:
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize image to 300x300 while maintaining aspect ratio
                    img.thumbnail((300, 300), PILImage.Resampling.LANCZOS)
                    
                    # Save the resized image
                    img.save(self.avatar.path, 'JPEG', quality=85)
            except Exception as e:
                print(f"Error resizing avatar: {e}")
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    @property
    def initials(self):
        """Get user's initials for avatar placeholder"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        return self.user.username[:2].upper()
    
    @property
    def has_avatar(self):
        """Check if user has a custom avatar"""
        return self.avatar and self.avatar.name != 'avatars/default.png'
    
    def get_search_content(self):
        """Return searchable content for the search index"""
        return {
            'title': self.full_name,
            'content': f"{self.full_name} {self.bio or ''} {self.company or ''} {self.position or ''} {self.location or ''}",
            'description': self.bio or f"Profile of {self.full_name}",
            'url': f'/profile/{self.user.username}/',
            'weight': 1,
            'is_public': True,
            'fields': {
                'username': self.user.username,
                'email': self.user.email,
                'company': self.company,
                'position': self.position,
                'location': self.location,
                'website': self.website,
                'has_avatar': self.has_avatar,
            }
        }

# Signal to automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
