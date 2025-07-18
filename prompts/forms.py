from django import forms
from django.contrib.auth.models import User
from .models import Prompt, Category, Tag, PromptCollection, PromptUsage
from django.db import models

class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = [
            'title', 'description', 'content', 'category', 'tags', 
            'prompt_type', 'difficulty', 'example_input', 'example_output', 
            'context_notes', 'is_public', 'is_featured', 'is_template'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Enter prompt title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Brief description of what this prompt does...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full font-mono',
                'rows': 8,
                'placeholder': 'Enter your prompt content here...'
            }),
            'category': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'select select-bordered w-full',
                'size': 5
            }),
            'prompt_type': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'example_input': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full font-mono',
                'rows': 4,
                'placeholder': 'Example input for the prompt...'
            }),
            'example_output': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full font-mono',
                'rows': 4,
                'placeholder': 'Example output from the prompt...'
            }),
            'context_notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Additional context or instructions...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-secondary'
            }),
            'is_template': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-accent'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter categories and tags if user is not staff
        if user and not user.is_staff:
            self.fields['category'].queryset = Category.objects.filter(
                prompts__is_public=True
            ).distinct()
            self.fields['tags'].queryset = Tag.objects.filter(
                prompts__is_public=True
            ).distinct()

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Category name...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Category description...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'color',
                'placeholder': '#3B82F6'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'light-bulb, code, cog, etc.'
            }),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Tag name...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'color',
                'placeholder': '#6B7280'
            }),
        }

class PromptCollectionForm(forms.ModelForm):
    class Meta:
        model = PromptCollection
        fields = ['name', 'description', 'prompts', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Collection name...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Collection description...'
            }),
            'prompts': forms.SelectMultiple(attrs={
                'class': 'select select-bordered w-full',
                'size': 8
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Only show prompts that the user can access
            if user.is_staff:
                self.fields['prompts'].queryset = Prompt.objects.all()
            else:
                self.fields['prompts'].queryset = Prompt.objects.filter(
                    models.Q(is_public=True) | models.Q(author=user)
                )

class PromptUsageForm(forms.ModelForm):
    class Meta:
        model = PromptUsage
        fields = ['input_text', 'output_text', 'rating', 'feedback']
        widgets = {
            'input_text': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full font-mono',
                'rows': 4,
                'placeholder': 'Your input text...'
            }),
            'output_text': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full font-mono',
                'rows': 6,
                'placeholder': 'Generated output...'
            }),
            'rating': forms.Select(attrs={
                'class': 'select select-bordered w-full'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Your feedback about this prompt...'
            }),
        }

class PromptSearchForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Search prompts...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    prompt_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Prompt.PROMPT_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    difficulty = forms.ChoiceField(
        choices=[('', 'All Difficulties')] + Prompt.DIFFICULTY_LEVELS,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'select select-bordered w-full',
            'size': 4
        })
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox checkbox-primary'
        })
    )
    
    is_template = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox checkbox-accent'
        })
    )

class PromptTestForm(forms.Form):
    input_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full font-mono',
            'rows': 6,
            'placeholder': 'Enter your input text here...'
        }),
        required=False
    )
    
    custom_prompt = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full font-mono',
            'rows': 4,
            'placeholder': 'Or enter a custom prompt...'
        }),
        required=False
    )
    
    model = forms.ChoiceField(
        choices=[
            ('gpt-4', 'GPT-4'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
            ('claude-3', 'Claude 3'),
            ('gemini-pro', 'Gemini Pro'),
        ],
        initial='gpt-3.5-turbo',
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full'
        })
    )
    
    temperature = forms.FloatField(
        min_value=0.0,
        max_value=2.0,
        initial=0.7,
        widget=forms.NumberInput(attrs={
            'class': 'input input-bordered w-full',
            'step': '0.1'
        })
    )
    
    max_tokens = forms.IntegerField(
        min_value=1,
        max_value=4000,
        initial=1000,
        widget=forms.NumberInput(attrs={
            'class': 'input input-bordered w-full'
        })
    ) 