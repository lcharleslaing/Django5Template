from django.db import models


class SongPrompt(models.Model):
    title = models.CharField(max_length=200, blank=True)
    lyrics = models.TextField(blank=True)
    subject = models.CharField(max_length=300, blank=True)
    styles = models.JSONField(default=list, help_text="List of styles, e.g., ['disco', 'rap', 'cinematic']")
    excluded_styles = models.JSONField(default=list, blank=True)
    weirdness = models.PositiveSmallIntegerField(default=50, help_text="0–100")
    style_influence = models.PositiveSmallIntegerField(default=50, help_text="0–100")
    is_instrumental = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def formatted_prompt(self):
        return {
            "title": self.title,
            "lyrics": self.lyrics or self.subject,
            "styles": self.styles,
            "excluded_styles": self.excluded_styles,
            "weirdness": self.weirdness,
            "style_influence": self.style_influence,
            "instrumental": self.is_instrumental
        }

    def __str__(self):
        return self.title or f"Untitled ({self.id})"

    class Meta:
        ordering = ['-created_at']