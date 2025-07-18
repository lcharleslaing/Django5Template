from django import forms
from .models import File

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 50MB.")
            
            # Check file extension
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.txt', '.rtf',
                '.xls', '.xlsx', '.csv',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
                '.zip', '.rar', '.7z',
                '.mp3', '.mp4', '.avi', '.mov'
            ]
            
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f"File type {ext} is not allowed.")
        
        return file 