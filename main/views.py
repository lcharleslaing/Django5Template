from django.shortcuts import render, redirect  # For rendering templates and redirects
from django.contrib.auth.forms import UserCreationForm  # Django's built-in user registration form
from django.contrib import messages  # For flash messages
from django.contrib.auth.decorators import login_required  # To require login for home view
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from files.models import File
from images.models import Image
from prompts.models import Prompt, Category, PromptUsage
from django.contrib.auth.models import User

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
    # Get current user
    user = request.user
    
    # Time ranges
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Get statistics
    context = {
        # User stats
        'total_files': File.objects.filter(uploaded_by=user).count(),
        'total_images': Image.objects.filter(uploaded_by=user).count(),
        'total_prompts': Prompt.objects.filter(author=user).count(),
        
        # Recent uploads (last 7 days)
        'recent_files': File.objects.filter(
            uploaded_by=user,
            uploaded_at__date__gte=last_week
        ).count(),
        'recent_images': Image.objects.filter(
            uploaded_by=user,
            uploaded_at__date__gte=last_week
        ).count(),
        
        # Latest items
        'latest_files': File.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:5],
        'latest_images': Image.objects.filter(uploaded_by=user).select_related('thumbnail').order_by('-uploaded_at')[:6],
        'latest_prompts': Prompt.objects.filter(author=user).select_related('category').order_by('-created_at')[:5],
        
        # Popular prompts (most used)
        'popular_prompts': Prompt.objects.filter(
            is_public=True
        ).order_by('-usage_count')[:5],
        
        # Featured prompts
        'featured_prompts': Prompt.objects.filter(
            is_featured=True,
            is_public=True
        ).select_related('category', 'author')[:3],
        
        # Prompt categories
        'categories': Category.objects.annotate(
            prompt_count=Count('prompts')
        ).order_by('-prompt_count')[:6],
        
        # Storage stats (simplified - you might want to calculate actual sizes)
        'storage_used': File.objects.filter(uploaded_by=user).count() + Image.objects.filter(uploaded_by=user).count(),
        
        # Activity chart data (last 7 days)
        'activity_data': get_activity_data(user, last_week, today),
        
        # Recent users (for admin)
        'recent_users': User.objects.order_by('-date_joined')[:5] if user.is_superuser else None,
    }
    
    return render(request, 'main/home.html', context)

def get_activity_data(user, start_date, end_date):
    """Get activity data for the dashboard chart"""
    activity_data = []
    current_date = start_date
    
    while current_date <= end_date:
        files_count = File.objects.filter(
            uploaded_by=user,
            uploaded_at__date=current_date
        ).count()
        
        images_count = Image.objects.filter(
            uploaded_by=user,
            uploaded_at__date=current_date
        ).count()
        
        prompts_count = Prompt.objects.filter(
            author=user,
            created_at__date=current_date
        ).count()
        
        activity_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'files': files_count,
            'images': images_count,
            'prompts': prompts_count,
            'total': files_count + images_count + prompts_count
        })
        
        current_date += timedelta(days=1)
    
    return activity_data
