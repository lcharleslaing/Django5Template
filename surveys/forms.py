from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Survey, Section, Question, Response, Answer, Invite


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'publish_start', 'publish_end', 'k_threshold']
        widgets = {
            'publish_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'publish_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        publish_start = cleaned_data.get('publish_start')
        publish_end = cleaned_data.get('publish_end')
        
        if publish_start and publish_end:
            if publish_start >= publish_end:
                raise ValidationError("Publish end date must be after publish start date.")
            
            if publish_start < timezone.now():
                raise ValidationError("Publish start date cannot be in the past.")
        
        return cleaned_data


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'type', 'prompt', 'help_text', 'required', 'anonymity_mode',
            'options_json', 'scale_min', 'scale_max', 'order', 'logic_json'
        ]
        widgets = {
            'prompt': forms.Textarea(attrs={'rows': 3}),
            'help_text': forms.Textarea(attrs={'rows': 2}),
            'options_json': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter JSON format options'}),
            'logic_json': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter JSON format logic'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('type')
        scale_min = cleaned_data.get('scale_min')
        scale_max = cleaned_data.get('scale_max')
        options_json = cleaned_data.get('options_json')
        
        # Validate scale for scale-based questions
        if question_type in ['LIKERT', 'NPS', 'NUMBER']:
            if scale_min is None or scale_max is None:
                raise ValidationError("Scale min and max are required for scale-based questions.")
            if scale_min >= scale_max:
                raise ValidationError("Scale max must be greater than scale min.")
            if scale_max - scale_min > 10:
                raise ValidationError("Scale range cannot exceed 10 points.")
        
        # Validate options for choice-based questions
        if question_type in ['MULTI', 'SINGLE', 'RANK']:
            if not options_json or not isinstance(options_json, dict):
                raise ValidationError("Options are required for choice-based questions.")
            choices = options_json.get('choices', [])
            if not choices or len(choices) < 2:
                raise ValidationError("At least 2 choices are required for choice-based questions.")
        
        return cleaned_data


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['cohort_json', 'meta_json']
        widgets = {
            'cohort_json': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter JSON format cohort data'}),
            'meta_json': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter JSON format metadata'}),
        }


class AnswerForm(forms.Form):
    """Dynamic form for answering questions based on question type"""
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self._build_fields()
    
    def _build_fields(self):
        """Build form fields based on question type"""
        question = self.question
        
        if question.type == 'LIKERT':
            choices = [(i, str(i)) for i in range(question.scale_min, question.scale_max + 1)]
            self.fields['value'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'NPS':
            choices = [(i, str(i)) for i in range(0, 11)]
            self.fields['value'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'MULTI':
            choices = [(opt, opt) for opt in question.options]
            self.fields['value'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'SINGLE':
            choices = [(opt, opt) for opt in question.options]
            self.fields['value'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'SHORT_TEXT':
            self.fields['value'] = forms.CharField(
                max_length=500,
                widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'LONG_TEXT':
            self.fields['value'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 4, 'class': 'textarea textarea-bordered w-full'}),
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'NUMBER':
            self.fields['value'] = forms.IntegerField(
                min_value=question.scale_min,
                max_value=question.scale_max,
                widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'DATE':
            self.fields['value'] = forms.DateField(
                widget=forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        elif question.type == 'RANK':
            choices = [(opt, opt) for opt in question.options]
            self.fields['value'] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={'class': 'select select-bordered w-full'}),
                required=question.required,
                label=question.prompt,
                help_text=question.help_text
            )
        
        # Add anonymity-specific fields for text questions
        if question.type in ['SHORT_TEXT', 'LONG_TEXT']:
            if question.anonymity_mode == 'ESCROW':
                self.fields['followup_opt_in'] = forms.BooleanField(
                    required=False,
                    initial=True,
                    label="I'm open to follow-up questions about this answer"
                )
                self.fields['preferred_contact'] = forms.CharField(
                    max_length=200,
                    required=False,
                    widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
                    label="Preferred contact method (optional)"
                )
            
            if question.anonymity_mode in ['ESCROW', 'SIGNED']:
                self.fields['is_signed'] = forms.BooleanField(
                    required=False,
                    initial=(question.anonymity_mode == 'SIGNED'),
                    label="Sign this answer with my name"
                )
    
    def clean_value(self):
        """Clean and validate the answer value"""
        value = self.cleaned_data.get('value')
        question = self.question
        
        if question.required and not value:
            raise ValidationError("This question is required.")
        
        # Type-specific validation
        if question.type == 'NUMBER':
            if value < question.scale_min or value > question.scale_max:
                raise ValidationError(f"Value must be between {question.scale_min} and {question.scale_max}.")
        
        return value


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ['email', 'expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            raise ValidationError("Expiration date must be in the future.")
        return expires_at


class BulkInviteForm(forms.Form):
    """Form for bulk inviting users to surveys"""
    SURVEY_CHOICES = []
    USER_CHOICES = []
    
    survey = forms.ModelChoiceField(
        queryset=Survey.objects.filter(status='PUBLISHED'),
        empty_label="Select a survey",
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )
    
    invite_type = forms.ChoiceField(
        choices=[
            ('all_users', 'All Users'),
            ('by_group', 'By Group'),
            ('manual_list', 'Manual Email List'),
        ],
        widget=forms.RadioSelect
    )
    
    # For manual email list
    email_list = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Enter email addresses, one per line',
            'class': 'textarea textarea-bordered w-full'
        }),
        required=False,
        help_text="Enter email addresses, one per line"
    )
    
    # For group selection
    groups = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Will be populated in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    
    expires_in_days = forms.IntegerField(
        min_value=1,
        max_value=30,
        initial=7,
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
        help_text="Invite expires in X days"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate user choices for group selection
        self.fields['groups'].queryset = User.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        invite_type = cleaned_data.get('invite_type')
        
        if invite_type == 'manual_list':
            email_list = cleaned_data.get('email_list', '').strip()
            if not email_list:
                raise ValidationError("Email list is required for manual invites.")
            
            # Validate email format
            emails = [email.strip() for email in email_list.split('\n') if email.strip()]
            for email in emails:
                if not forms.EmailField().clean(email):
                    raise ValidationError(f"Invalid email format: {email}")
        
        elif invite_type == 'by_group':
            groups = cleaned_data.get('groups')
            if not groups:
                raise ValidationError("Please select at least one group for group-based invites.")
        
        return cleaned_data


class SurveyReportForm(forms.Form):
    """Form for generating survey reports"""
    REPORT_TYPES = [
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('cohort', 'Cohort Analysis'),
        ('sentiment', 'Sentiment Analysis'),
    ]
    
    EXPORT_FORMATS = [
        ('html', 'HTML'),
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.RadioSelect,
        initial='summary'
    )
    
    export_format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'}),
        initial='html'
    )
    
    include_anonymous = forms.BooleanField(
        required=False,
        initial=True,
        label="Include anonymous responses in aggregates"
    )
    
    min_cohort_size = forms.IntegerField(
        min_value=1,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
        help_text="Minimum cohort size for detailed breakdowns (k-anonymity)"
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
        help_text="Filter responses from this date (optional)"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full'}),
        help_text="Filter responses until this date (optional)"
    )
