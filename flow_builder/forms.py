from django import forms
from .models import Flow, Step, Task, Person, Department


class FlowForm(forms.ModelForm):
    class Meta:
        model = Flow
        fields = ['name', 'description', 'start_date', 'is_active']


class StepForm(forms.ModelForm):
    dependencies = forms.ModelMultipleChoiceField(
        queryset=Step.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select steps that must complete before this one starts"
    )
    
    class Meta:
        model = Step
        fields = ['title', 'description', 'time_allotted_days']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        flow = kwargs.pop('flow', None)
        super().__init__(*args, **kwargs)
        
        if flow:
            # Set queryset for dependencies to only include steps from the same flow
            self.fields['dependencies'].queryset = flow.steps.all()
            
            # If editing an existing step, exclude it from dependencies
            if self.instance and self.instance.pk:
                self.fields['dependencies'].queryset = flow.steps.exclude(pk=self.instance.pk)
    
    def save(self, commit=True):
        step = super().save(commit=False)
        if commit:
            step.save()
            # Handle dependencies
            if 'dependencies' in self.cleaned_data:
                step.dependencies.set(self.cleaned_data['dependencies'])
        return step


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'responsible_person', 'due_date', 'is_completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'responsible_person': forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for responsible_person to all people
        self.fields['responsible_person'].queryset = Person.objects.all()
        self.fields['responsible_person'].empty_label = "Select a person (optional)"
