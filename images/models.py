from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image as PILImage
import os

class Image(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    thumbnail = models.ImageField(upload_to='images/thumbnails/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('images:image_detail', kwargs={'image_id': self.pk})

    def save(self, *args, **kwargs):
        # Save first to ensure the file is written to disk
        super().save(*args, **kwargs)

        # Calculate file size and dimensions after saving
        if self.image:
            self.file_size = self.image.size

            # Open image to get dimensions
            with PILImage.open(self.image.path) as img:
                self.width = img.width
                self.height = img.height

                # Create thumbnail if it doesn't exist
                if not self.thumbnail:
                    self.create_thumbnail()

                # Save again to update the dimensions and thumbnail
                super().save(update_fields=['width', 'height', 'thumbnail'])

    def create_thumbnail(self):
        """Create a thumbnail version of the image"""
        if self.image:
            with PILImage.open(self.image.path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create thumbnail (max 200x200)
                img.thumbnail((200, 200), PILImage.Resampling.LANCZOS)

                # Save thumbnail
                thumb_filename = f'thumb_{os.path.basename(self.image.name)}'
                thumb_path = f'images/thumbnails/{thumb_filename}'

                # Use Django's storage to save the thumbnail
                from django.core.files.base import ContentFile
                import io

                # Save image to bytes
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)

                # Save to Django storage
                self.thumbnail.save(thumb_filename, ContentFile(buffer.getvalue()), save=False)

    def filename(self):
        return os.path.basename(self.image.name)

    def file_extension(self):
        name, extension = os.path.splitext(self.image.name)
        return extension.lower()

    def aspect_ratio(self):
        if self.width and self.height:
            return self.width / self.height
        return None
