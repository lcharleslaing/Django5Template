from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            'name', 'provider', 'amount', 'billing_cycle', 'start_date', 'next_due_date',
            'notes', 'is_active', 'is_api_enabled', 'api_base_url', 'api_key', 'api_token'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'textarea textarea-bordered w-full'}),
            'api_token': forms.Textarea(attrs={'rows': 2, 'class': 'textarea textarea-bordered w-full'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
            'next_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'provider': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'amount': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'billing_cycle': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'api_base_url': forms.URLInput(attrs={'class': 'input input-bordered w-full'}),
            'api_key': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        }