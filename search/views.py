from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.utils.html import strip_tags
import json
import re
from .models import SearchIndex, SearchHistory, SearchSuggestion

def search_view(request):
    """Main search view with results"""
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    app_filter = request.GET.get('app', '')
    model_filter = request.GET.get('model', '')
    
    results = []
    total_results = 0
    
    if query:
        # Build search query
        search_query = Q(title__icontains=query) | Q(content__icontains=query) | Q(description__icontains=query)
        
        # Add filters
        if app_filter:
            search_query &= Q(app_name=app_filter)
        if model_filter:
            search_query &= Q(model_name=model_filter)
        
        # Get results
        results = SearchIndex.objects.filter(search_query, is_public=True).order_by('-search_weight', '-created_at')
        total_results = results.count()
        
        # Pagination
        paginator = Paginator(results, 20)
        results = paginator.get_page(page)
        
        # Log search
        SearchHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query,
            results_count=total_results,
            session_id=request.session.session_key
        )
        
        # Update search suggestions
        suggestion, created = SearchSuggestion.objects.get_or_create(term=query.lower())
        if not created:
            suggestion.frequency += 1
            suggestion.save()
    
    # Get available apps and models for filtering
    apps = SearchIndex.objects.values_list('app_name', flat=True).distinct()
    models = SearchIndex.objects.values_list('model_name', flat=True).distinct()
    
    # Get popular searches
    popular_searches = SearchSuggestion.objects.filter(is_featured=True)[:10]
    
    context = {
        'query': query,
        'results': results,
        'total_results': total_results,
        'apps': apps,
        'models': models,
        'app_filter': app_filter,
        'model_filter': model_filter,
        'popular_searches': popular_searches,
    }
    
    return render(request, 'search/search.html', context)

def search_api(request):
    """AJAX API for real-time search results"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    
    if not query or len(query) < 2:
        return JsonResponse({'results': [], 'total': 0})
    
    # Search in title, content, and description
    search_query = Q(title__icontains=query) | Q(content__icontains=query) | Q(description__icontains=query)
    
    # Get results
    results = SearchIndex.objects.filter(search_query, is_public=True).order_by('-search_weight', '-created_at')[:limit]
    
    # Format results for JSON
    formatted_results = []
    for result in results:
        # Highlight search terms in content
        highlighted_content = highlight_search_terms(result.content, query)
        highlighted_title = highlight_search_terms(result.title, query)
        
        formatted_results.append({
            'id': result.id,
            'title': result.title,
            'highlighted_title': highlighted_title,
            'content': result.content[:200] + '...' if len(result.content) > 200 else result.content,
            'highlighted_content': highlighted_content,
            'description': result.description,
            'url': result.get_absolute_url(),
            'app_name': result.app_name,
            'model_name': result.model_name,
            'icon': result.get_icon(),
            'color': result.get_color(),
            'created_at': result.created_at.strftime('%Y-%m-%d'),
            'created_by': result.created_by.username if result.created_by else None,
        })
    
    return JsonResponse({
        'results': formatted_results,
        'total': len(formatted_results),
        'query': query
    })

def search_suggestions(request):
    """Get search suggestions based on popular searches and user history"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Get popular searches that match the query
    popular = SearchSuggestion.objects.filter(
        term__icontains=query
    ).order_by('-frequency', '-last_searched')[:5]
    
    for suggestion in popular:
        suggestions.append({
            'term': suggestion.term,
            'type': 'popular',
            'frequency': suggestion.frequency
        })
    
    # Get user's recent searches
    if request.user.is_authenticated:
        recent = SearchHistory.objects.filter(
            user=request.user,
            query__icontains=query
        ).order_by('-created_at')[:3]
        
        for history in recent:
            if history.query not in [s['term'] for s in suggestions]:
                suggestions.append({
                    'term': history.query,
                    'type': 'recent',
                    'date': history.created_at.strftime('%Y-%m-%d')
                })
    
    return JsonResponse({'suggestions': suggestions[:8]})

def search_autocomplete(request):
    """Autocomplete for search terms"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Get unique search terms from history
    suggestions = SearchHistory.objects.filter(
        query__icontains=query
    ).values('query').distinct().order_by('-created_at')[:10]
    
    return JsonResponse({
        'suggestions': [s['query'] for s in suggestions]
    })

def highlight_search_terms(text, query):
    """Highlight search terms in text"""
    if not text or not query:
        return text
    
    # Split query into words
    words = query.split()
    
    # Create regex pattern for case-insensitive matching
    pattern = '|'.join(re.escape(word) for word in words)
    
    # Replace matches with highlighted version
    highlighted = re.sub(
        f'({pattern})',
        r'<mark class="bg-yellow-200 dark:bg-yellow-800">\1</mark>',
        text,
        flags=re.IGNORECASE
    )
    
    return highlighted

def search_stats(request):
    """Get search statistics for dashboard"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    # Total indexed items
    total_items = SearchIndex.objects.count()
    
    # Items by app
    items_by_app = {}
    for app in SearchIndex.objects.values('app_name').distinct():
        app_name = app['app_name']
        count = SearchIndex.objects.filter(app_name=app_name).count()
        items_by_app[app_name] = count
    
    # Recent searches
    recent_searches = SearchHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Popular searches
    popular_searches = SearchSuggestion.objects.order_by('-frequency')[:10]
    
    return JsonResponse({
        'total_items': total_items,
        'items_by_app': items_by_app,
        'recent_searches': [
            {
                'query': search.query,
                'date': search.created_at.strftime('%Y-%m-%d %H:%M'),
                'results_count': search.results_count
            }
            for search in recent_searches
        ],
        'popular_searches': [
            {
                'term': suggestion.term,
                'frequency': suggestion.frequency
            }
            for suggestion in popular_searches
        ]
    })

@login_required
def rebuild_search_index(request):
    """Rebuild the search index from all apps"""
    from django.apps import apps
    
    # Clear existing index
    SearchIndex.objects.all().delete()
    
    # Get all models from all apps
    indexed_count = 0
    
    for app_config in apps.get_app_configs():
        app_name = app_config.label
        
        # Skip Django's built-in apps and our search app
        if app_name in ['admin', 'auth', 'contenttypes', 'sessions', 'search']:
            continue
        
        for model in app_config.get_models():
            model_name = model.__name__
            
            # Check if model has searchable fields
            if hasattr(model, 'get_search_content'):
                # Use custom search method
                for obj in model.objects.all():
                    try:
                        search_data = obj.get_search_content()
                        SearchIndex.objects.create(
                            content_type=ContentType.objects.get_for_model(model),
                            object_id=obj.id,
                            title=search_data.get('title', str(obj)),
                            content=search_data.get('content', ''),
                            description=search_data.get('description', ''),
                            app_name=app_name,
                            model_name=model_name,
                            url=search_data.get('url', ''),
                            created_by=getattr(obj, 'created_by', None) or getattr(obj, 'uploaded_by', None) or getattr(obj, 'author', None),
                            search_weight=search_data.get('weight', 1),
                            is_public=search_data.get('is_public', True),
                            searchable_fields=search_data.get('fields', {})
                        )
                        indexed_count += 1
                    except Exception as e:
                        print(f"Error indexing {app_name}.{model_name} {obj.id}: {e}")
            else:
                # Default indexing for common fields
                searchable_fields = ['title', 'name', 'description', 'content']
                available_fields = [f.name for f in model._meta.fields if f.name in searchable_fields]
                
                if available_fields:
                    for obj in model.objects.all():
                        try:
                            title = getattr(obj, 'title', None) or getattr(obj, 'name', None) or str(obj)
                            content = ' '.join([
                                str(getattr(obj, field, '')) 
                                for field in available_fields 
                                if getattr(obj, field, None)
                            ])
                            
                            if title and content:
                                SearchIndex.objects.create(
                                    content_type=ContentType.objects.get_for_model(model),
                                    object_id=obj.id,
                                    title=title,
                                    content=content,
                                    description=getattr(obj, 'description', ''),
                                    app_name=app_name,
                                    model_name=model_name,
                                    created_by=getattr(obj, 'created_by', None) or getattr(obj, 'uploaded_by', None) or getattr(obj, 'author', None),
                                    is_public=True
                                )
                                indexed_count += 1
                        except Exception as e:
                            print(f"Error indexing {app_name}.{model_name} {obj.id}: {e}")
    
    return JsonResponse({
        'success': True,
        'indexed_count': indexed_count,
        'message': f'Successfully indexed {indexed_count} items'
    })