from django.shortcuts import render, redirect  # For rendering templates and redirects
from django.contrib.auth.forms import UserCreationForm  # Django's built-in user registration form
from django.contrib import messages  # For flash messages
from django.contrib.auth.decorators import login_required  # To require login for home view
from django.http import JsonResponse
from django.db.models import Q, Count
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import json
from datetime import datetime, timedelta
from django.utils import timezone

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
# Renders modern dashboard with comprehensive statistics

@login_required
def home(request):
    # Get dashboard statistics
    stats = get_dashboard_stats()
    
    # Get recent activity
    recent_activity = get_recent_activity()
    
    context = {
        'stats': stats,
        'recent_activity': recent_activity,
    }
    return render(request, 'main/dashboard.html', context)

def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    stats = {}
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    new_users_this_month = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=30)).count()
    
    stats['users'] = {
        'total': total_users,
        'active': active_users,
        'new_this_month': new_users_this_month,
    }
    
    # Get statistics for all models dynamically
    for model in apps.get_models():
        if hasattr(model, '_meta'):
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            
            # Skip Django's built-in models
            if app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                continue
                
            try:
                total_count = model.objects.count()
                
                # Try to get recent items (assuming created_at or uploaded_at field)
                recent_count = 0
                if hasattr(model, 'created_at'):
                    recent_count = model.objects.filter(
                        created_at__gte=timezone.now() - timedelta(days=7)
                    ).count()
                elif hasattr(model, 'uploaded_at'):
                    recent_count = model.objects.filter(
                        uploaded_at__gte=timezone.now() - timedelta(days=7)
                    ).count()
                elif hasattr(model, 'date_joined'):
                    recent_count = model.objects.filter(
                        date_joined__gte=timezone.now() - timedelta(days=7)
                    ).count()
                
                if app_label not in stats:
                    stats[app_label] = {}
                
                stats[app_label][model_name] = {
                    'total': total_count,
                    'recent': recent_count,
                    'model': model,
                }
            except Exception:
                continue
    
    return stats

def get_recent_activity():
    """Get recent activity across all models"""
    activities = []
    
    # Get recent activities from different models
    for model in apps.get_models():
        if hasattr(model, '_meta'):
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            
            # Skip Django's built-in models
            if app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                continue
            
            try:
                # Get recent items
                recent_items = None
                if hasattr(model, 'created_at'):
                    recent_items = model.objects.order_by('-created_at')[:5]
                elif hasattr(model, 'uploaded_at'):
                    recent_items = model.objects.order_by('-uploaded_at')[:5]
                elif hasattr(model, 'updated_at'):
                    recent_items = model.objects.order_by('-updated_at')[:5]
                
                if recent_items:
                    for item in recent_items:
                        activity_time = None
                        if hasattr(item, 'created_at'):
                            activity_time = item.created_at
                        elif hasattr(item, 'uploaded_at'):
                            activity_time = item.uploaded_at
                        elif hasattr(item, 'updated_at'):
                            activity_time = item.updated_at
                        
                        if activity_time:
                            activities.append({
                                'type': model_name,
                                'app': app_label,
                                'title': str(item),
                                'time': activity_time,
                                'id': item.pk,
                            })
            except Exception:
                continue
    
    # Sort by time and return most recent 20
    activities.sort(key=lambda x: x['time'], reverse=True)
    return activities[:20]

@login_required
def search_api(request):
    """Comprehensive search API that searches across all models"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Search across all models dynamically
    for model in apps.get_models():
        if hasattr(model, '_meta'):
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            
            # Skip Django's built-in models
            if app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                continue
            
            try:
                # Build search query dynamically
                search_fields = []
                
                # Get all text fields for searching
                for field in model._meta.fields:
                    if field.get_internal_type() in ['CharField', 'TextField']:
                        search_fields.append(field.name)
                
                if search_fields:
                    # Build Q object for OR search across all text fields
                    q_objects = Q()
                    for field in search_fields:
                        q_objects |= Q(**{f'{field}__icontains': query})
                    
                    # Execute search
                    matches = model.objects.filter(q_objects)[:10]
                    
                    for match in matches:
                        # Try to get the best URL for the item
                        url = '#'
                        if hasattr(match, 'get_absolute_url'):
                            url = match.get_absolute_url()
                        else:
                            # Generate URL based on app and model patterns
                            try:
                                url = f'/{app_label}s/{match.pk}/'
                            except:
                                url = '#'
                        
                        # Get description from the model
                        description = ''
                        if hasattr(match, 'description') and match.description:
                            description = match.description[:100] + '...' if len(match.description) > 100 else match.description
                        elif hasattr(match, 'bio') and match.bio:
                            description = match.bio[:100] + '...' if len(match.bio) > 100 else match.bio
                        
                        results.append({
                            'title': str(match),
                            'description': description,
                            'type': model_name.replace('_', ' ').title(),
                            'app': app_label.title(),
                            'url': url,
                            'id': match.pk,
                        })
            
            except Exception as e:
                # Skip models that can't be searched
                continue
    
    # Sort results by relevance (title matches first)
    results.sort(key=lambda x: (
        0 if query.lower() in x['title'].lower() else 1,
        x['title'].lower()
    ))
    
    return JsonResponse({'results': results[:50]})  # Limit to 50 results
