from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone', 'company', 'position', 'website', 'location', 'date_of_birth']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'bio': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'phone': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '+1 (555) 123-4567'}),
            'company': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Your Company'}),
            'position': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Your Position'}),
            'website': forms.URLInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'https://yourwebsite.com'}),
            'location': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'City, State/Country'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
        }
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (max 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Avatar image must be under 5MB.")
            
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            import os
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f"Avatar must be one of: {', '.join(allowed_extensions)}")
        
        return avatar

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'email@example.com'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email address is already in use.")
        return email

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Current Password'}),
        label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'New Password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Confirm New Password'}),
        label='Confirm New Password'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password is incorrect.")
        return current_password
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
            
            # Check password strength
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return password2
    
    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user 