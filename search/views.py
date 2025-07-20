from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.models import User
from files.models import File
from images.models import Image
from prompts.models import Prompt, Category, Tag
from userprofile.models import UserProfile
import json

@login_required
def search_view(request):
    """Main search view that handles both regular and AJAX requests"""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')
    
    results = {
        'files': [],
        'images': [],
        'prompts': [],
        'users': [],
        'categories': [],
        'tags': []
    }
    
    if query:
        # Search Files
        if search_type in ['all', 'files']:
            files = File.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(filename__icontains=query)
            ).select_related('uploaded_by')[:20]
            
            results['files'] = [{
                'id': file.id,
                'title': file.title,
                'description': file.description or '',
                'filename': file.filename(),
                'uploaded_by': file.uploaded_by.username,
                'uploaded_at': file.uploaded_at.strftime('%Y-%m-%d'),
                'url': f'/files/{file.id}/'
            } for file in files]
        
        # Search Images
        if search_type in ['all', 'images']:
            images = Image.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            ).select_related('uploaded_by')[:20]
            
            results['images'] = [{
                'id': image.id,
                'title': image.title,
                'description': image.description or '',
                'uploaded_by': image.uploaded_by.username,
                'uploaded_at': image.uploaded_at.strftime('%Y-%m-%d'),
                'thumbnail': image.thumbnail.url if image.thumbnail else '',
                'url': f'/images/{image.id}/'
            } for image in images]
        
        # Search Prompts
        if search_type in ['all', 'prompts']:
            prompts = Prompt.objects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).select_related('author', 'category').distinct()[:20]
            
            results['prompts'] = [{
                'id': prompt.id,
                'title': prompt.title,
                'description': prompt.short_description,
                'category': prompt.category.name,
                'author': prompt.author.username,
                'type': prompt.get_prompt_type_display(),
                'difficulty': prompt.get_difficulty_display(),
                'url': prompt.get_absolute_url()
            } for prompt in prompts]
        
        # Search Users
        if search_type in ['all', 'users']:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            ).select_related('profile')[:20]
            
            results['users'] = [{
                'id': user.id,
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'avatar': user.profile.avatar.url if hasattr(user, 'profile') and user.profile.avatar else '',
                'url': f'/profile/{user.username}/'
            } for user in users]
        
        # Search Categories
        if search_type in ['all', 'prompts']:
            categories = Category.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            
            results['categories'] = [{
                'id': cat.id,
                'name': cat.name,
                'description': cat.description or '',
                'color': cat.color,
                'icon': cat.icon,
                'url': cat.get_absolute_url()
            } for cat in categories]
        
        # Search Tags
        if search_type in ['all', 'prompts']:
            tags = Tag.objects.filter(name__icontains=query)[:10]
            
            results['tags'] = [{
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'url': f'/prompts/tag/{tag.name}/'
            } for tag in tags]
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'query': query,
            'results': results,
            'total_count': sum(len(items) for items in results.values())
        })
    
    # Return template for regular requests
    return render(request, 'search/results.html', {
        'query': query,
        'results': results,
        'search_type': search_type
    })

@login_required
def quick_search(request):
    """Quick search endpoint for Ctrl+K functionality"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    results = []
    
    # Quick search across all models
    # Files
    files = File.objects.filter(
        Q(title__icontains=query) | Q(filename__icontains=query)
    ).select_related('uploaded_by')[:5]
    
    for file in files:
        results.append({
            'type': 'file',
            'title': file.title,
            'subtitle': f'File • {file.filename()}',
            'icon': 'document',
            'url': f'/files/{file.id}/'
        })
    
    # Images
    images = Image.objects.filter(title__icontains=query)[:5]
    
    for image in images:
        results.append({
            'type': 'image',
            'title': image.title,
            'subtitle': f'Image • {image.uploaded_by.username}',
            'icon': 'photograph',
            'url': f'/images/{image.id}/'
        })
    
    # Prompts
    prompts = Prompt.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).select_related('category')[:5]
    
    for prompt in prompts:
        results.append({
            'type': 'prompt',
            'title': prompt.title,
            'subtitle': f'Prompt • {prompt.category.name}',
            'icon': 'light-bulb',
            'url': prompt.get_absolute_url()
        })
    
    # Users
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:3]
    
    for user in users:
        results.append({
            'type': 'user',
            'title': user.get_full_name() or user.username,
            'subtitle': f'User • @{user.username}',
            'icon': 'user',
            'url': f'/profile/{user.username}/'
        })
    
    return JsonResponse({
        'results': results[:15]  # Limit total results
    })
