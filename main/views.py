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
    """Dashboard homepage that shows aggregated statistics across all models."""
    from django.apps import apps

    model_stats = []
    for model in apps.get_models():
        meta = model._meta
        try:
            count = model.objects.count()
        except Exception:
            # Unmanaged or abstract models may raise errors
            continue

        model_stats.append({
            'label': meta.verbose_name_plural.title(),
            'count': count,
            'app_label': meta.app_label,
            'model_name': meta.model_name,
            'admin_url': f"/admin/{meta.app_label}/{meta.model_name}/"  # Quick link to admin list
        })

    # Sort by count descending and show top 8 to keep UI tidy
    model_stats.sort(key=lambda x: x['count'], reverse=True)

    context = {
        'model_stats': model_stats[:8],
    }

    return render(request, 'main/dashboard.html', context)
