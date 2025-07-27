from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import os

# Create your models here.

class File(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='files/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('files:file_detail', kwargs={'file_id': self.pk})

    def save(self, *args, **kwargs):
        # Calculate file size before saving
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def filename(self):
        return os.path.basename(self.file.name)

    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

    def is_image(self):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return self.file_extension() in image_extensions

    def is_pdf(self):
        return self.file_extension() == '.pdf'

    def is_document(self):
        doc_extensions = ['.doc', '.docx', '.txt', '.rtf']
        return self.file_extension() in doc_extensions

    def is_spreadsheet(self):
        spreadsheet_extensions = ['.xls', '.xlsx', '.csv']
        return self.file_extension() in spreadsheet_extensions
