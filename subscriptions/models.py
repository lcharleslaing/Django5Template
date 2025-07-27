from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Subscription(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    start_date = models.DateField()
    next_due_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_api_enabled = models.BooleanField(default=False)

    # API fields
    api_base_url = models.URLField(blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_token = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.amount})"

    def get_absolute_url(self):
        return reverse('subscriptions:subscription_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
