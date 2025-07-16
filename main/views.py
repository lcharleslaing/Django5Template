from django.shortcuts import render, redirect  # For rendering templates and redirects
from django.contrib.auth.forms import UserCreationForm  # Django's built-in user registration form
from django.contrib import messages  # For flash messages
from django.contrib.auth.decorators import login_required  # To require login for home view

# User registration view
# Handles GET (show form) and POST (process form) requests
# On successful registration, redirects to login page with a success message
# Renders 'registration/register.html' template

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Home view, requires user to be logged in
# Renders 'home.html' template

@login_required
def home(request):
    return render(request, 'home.html')
