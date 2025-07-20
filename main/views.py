from django.shortcuts import render, redirect  # For rendering templates and redirects
from django.contrib.auth.forms import UserCreationForm  # Django's built-in user registration form
from django.contrib import messages  # For flash messages
from django.contrib.auth.decorators import login_required  # To require login for home view
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

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
    # Import models here to avoid circular imports
    try:
        from files.models import File
        from images.models import Image
        from prompts.models import Prompt, Category
        from userprofile.models import UserProfile
        from search.models import SearchIndex, SearchHistory
        
        # Get user's data
        user = request.user
        
        # Recent files
        recent_files = File.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:5]
        
        # Recent images
        recent_images = Image.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:5]
        
        # Recent prompts
        recent_prompts = Prompt.objects.filter(author=user).order_by('-created_at')[:5]
        
        # Popular categories
        popular_categories = Category.objects.annotate(
            prompt_count=Count('prompts')
        ).order_by('-prompt_count')[:6]
        
        # User's recent searches
        recent_searches = SearchHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Statistics
        stats = {
            'total_files': File.objects.filter(uploaded_by=user).count(),
            'total_images': Image.objects.filter(uploaded_by=user).count(),
            'total_prompts': Prompt.objects.filter(author=user).count(),
            'total_searches': SearchHistory.objects.filter(user=user).count(),
        }
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_activity = []
        
        # Add recent files
        for file in File.objects.filter(uploaded_by=user, uploaded_at__gte=week_ago)[:3]:
            recent_activity.append({
                'type': 'file',
                'title': file.title,
                'date': file.uploaded_at,
                'url': f'/files/{file.id}/',
                'icon': 'document',
                'color': 'blue'
            })
        
        # Add recent images
        for image in Image.objects.filter(uploaded_by=user, uploaded_at__gte=week_ago)[:3]:
            recent_activity.append({
                'type': 'image',
                'title': image.title,
                'date': image.uploaded_at,
                'url': f'/images/{image.id}/',
                'icon': 'photo',
                'color': 'green'
            })
        
        # Add recent prompts
        for prompt in Prompt.objects.filter(author=user, created_at__gte=week_ago)[:3]:
            recent_activity.append({
                'type': 'prompt',
                'title': prompt.title,
                'date': prompt.created_at,
                'url': f'/prompts/{prompt.slug}/',
                'icon': 'light-bulb',
                'color': 'purple'
            })
        
        # Sort by date
        recent_activity.sort(key=lambda x: x['date'], reverse=True)
        recent_activity = recent_activity[:6]
        
        # Quick actions
        quick_actions = [
            {
                'title': 'Upload File',
                'description': 'Add a new file to your collection',
                'url': '/files/upload/',
                'icon': 'document-plus',
                'color': 'blue'
            },
            {
                'title': 'Upload Image',
                'description': 'Add a new image to your gallery',
                'url': '/images/upload/',
                'icon': 'photo-plus',
                'color': 'green'
            },
            {
                'title': 'Create Prompt',
                'description': 'Create a new AI prompt',
                'url': '/prompts/create/',
                'icon': 'light-bulb-plus',
                'color': 'purple'
            },
            {
                'title': 'View Profile',
                'description': 'Update your profile information',
                'url': '/profile/',
                'icon': 'user',
                'color': 'orange'
            }
        ]
        
        context = {
            'recent_files': recent_files,
            'recent_images': recent_images,
            'recent_prompts': recent_prompts,
            'popular_categories': popular_categories,
            'recent_searches': recent_searches,
            'stats': stats,
            'recent_activity': recent_activity,
            'quick_actions': quick_actions,
        }
        
    except ImportError:
        # If models don't exist yet, provide empty context
        context = {
            'recent_files': [],
            'recent_images': [],
            'recent_prompts': [],
            'popular_categories': [],
            'recent_searches': [],
            'stats': {'total_files': 0, 'total_images': 0, 'total_prompts': 0, 'total_searches': 0},
            'recent_activity': [],
            'quick_actions': [],
        }
    
    return render(request, 'main/home.html', context)
