from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Prompt, Category, Tag, PromptCollection, PromptUsage
from .forms import (
    PromptForm, CategoryForm, TagForm, PromptCollectionForm, 
    PromptUsageForm, PromptSearchForm, PromptTestForm
)

def test_view(request):
    """Test view to check template loading"""
    return render(request, 'prompts/test.html')

def prompt_list(request):
    """Display list of prompts with search and filtering"""
    search_form = PromptSearchForm(request.GET)
    prompts = Prompt.objects.filter(is_public=True)
    
    # Apply search filters
    if search_form.is_valid():
        q = search_form.cleaned_data.get('q')
        if q:
            prompts = prompts.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) | 
                Q(content__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
        
        category = search_form.cleaned_data.get('category')
        if category:
            prompts = prompts.filter(category=category)
        
        prompt_type = search_form.cleaned_data.get('prompt_type')
        if prompt_type:
            prompts = prompts.filter(prompt_type=prompt_type)
        
        difficulty = search_form.cleaned_data.get('difficulty')
        if difficulty:
            prompts = prompts.filter(difficulty=difficulty)
        
        tags = search_form.cleaned_data.get('tags')
        if tags:
            prompts = prompts.filter(tags__in=tags).distinct()
        
        if search_form.cleaned_data.get('is_featured'):
            prompts = prompts.filter(is_featured=True)
        
        if search_form.cleaned_data.get('is_template'):
            prompts = prompts.filter(is_template=True)
    
    # Get categories and tags for sidebar
    categories = Category.objects.annotate(prompt_count=Count('prompts')).order_by('-prompt_count')[:10]
    popular_tags = Tag.objects.annotate(prompt_count=Count('prompts')).order_by('-prompt_count')[:15]
    
    # Pagination
    paginator = Paginator(prompts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories,
        'popular_tags': popular_tags,
        'featured_prompts': Prompt.objects.filter(is_featured=True, is_public=True)[:3],
    }
    return render(request, 'prompts/prompt_list.html', context)

def prompt_detail(request, slug):
    """Display prompt details and allow testing"""
    prompt = get_object_or_404(Prompt, slug=slug, is_public=True)
    test_form = PromptTestForm()
    usage_form = PromptUsageForm()
    
    # Get related prompts
    related_prompts = Prompt.objects.filter(
        category=prompt.category,
        is_public=True
    ).exclude(id=prompt.id)[:4]
    
    # Track view (increment usage count)
    if request.user.is_authenticated:
        prompt.increment_usage()
    
    context = {
        'prompt': prompt,
        'test_form': test_form,
        'usage_form': usage_form,
        'related_prompts': related_prompts,
    }
    return render(request, 'prompts/prompt_detail.html', context)

@login_required
def prompt_create(request):
    """Create a new prompt"""
    if request.method == 'POST':
        form = PromptForm(request.POST, user=request.user)
        if form.is_valid():
            prompt = form.save(commit=False)
            prompt.author = request.user
            prompt.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Prompt created successfully!')
            return redirect('prompts:prompt_detail', slug=prompt.slug)
    else:
        form = PromptForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Prompt',
    }
    return render(request, 'prompts/prompt_form.html', context)

@login_required
def prompt_edit(request, slug):
    """Edit an existing prompt"""
    prompt = get_object_or_404(Prompt, slug=slug)
    
    # Check permissions
    if not request.user.is_staff and prompt.author != request.user:
        messages.error(request, "You don't have permission to edit this prompt.")
        return redirect('prompts:prompt_detail', slug=slug)
    
    if request.method == 'POST':
        form = PromptForm(request.POST, instance=prompt, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prompt updated successfully!')
            return redirect('prompts:prompt_detail', slug=prompt.slug)
    else:
        form = PromptForm(instance=prompt, user=request.user)
    
    context = {
        'form': form,
        'prompt': prompt,
        'title': 'Edit Prompt',
    }
    return render(request, 'prompts/prompt_form.html', context)

@login_required
@require_POST
def prompt_delete(request, slug):
    """Delete a prompt"""
    prompt = get_object_or_404(Prompt, slug=slug)
    
    # Check permissions
    if not request.user.is_staff and prompt.author != request.user:
        messages.error(request, "You don't have permission to delete this prompt.")
        return redirect('prompts:prompt_detail', slug=slug)
    
    prompt.delete()
    messages.success(request, 'Prompt deleted successfully!')
    return redirect('prompts:prompt_list')

@login_required
def prompt_test(request, slug):
    """Test a prompt with AI"""
    prompt = get_object_or_404(Prompt, slug=slug, is_public=True)
    
    if request.method == 'POST':
        form = PromptTestForm(request.POST)
        if form.is_valid():
            # Here you would integrate with your AI service
            # For now, we'll just simulate a response
            input_text = form.cleaned_data.get('input_text', '')
            custom_prompt = form.cleaned_data.get('custom_prompt', '')
            
            # Use custom prompt if provided, otherwise use the prompt's content
            final_prompt = custom_prompt if custom_prompt else prompt.content
            
            # Simulate AI response (replace with actual AI integration)
            simulated_response = f"""
This is a simulated response to your prompt:

**Prompt:** {final_prompt}

**Input:** {input_text if input_text else 'No input provided'}

**Response:** This is where the actual AI response would appear. In a real implementation, you would integrate with OpenAI, Claude, or another AI service here.

**Model used:** {form.cleaned_data.get('model')}
**Temperature:** {form.cleaned_data.get('temperature')}
**Max tokens:** {form.cleaned_data.get('max_tokens')}
"""
            
            # Create usage record
            usage = PromptUsage.objects.create(
                prompt=prompt,
                user=request.user,
                input_text=input_text,
                output_text=simulated_response,
            )
            
            context = {
                'prompt': prompt,
                'form': form,
                'response': simulated_response,
                'usage': usage,
            }
            return render(request, 'prompts/prompt_test_result.html', context)
    else:
        form = PromptTestForm()
    
    context = {
        'prompt': prompt,
        'form': form,
    }
    return render(request, 'prompts/prompt_test.html', context)

@login_required
@require_POST
def prompt_rate(request, slug):
    """Rate a prompt after using it"""
    prompt = get_object_or_404(Prompt, slug=slug)
    usage_id = request.POST.get('usage_id')
    
    if usage_id:
        usage = get_object_or_404(PromptUsage, id=usage_id, user=request.user)
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback', '')
        
        if rating:
            usage.rating = int(rating)
            usage.feedback = feedback
            usage.save()
            
            # Update prompt's average rating
            prompt.update_rating(int(rating))
            
            messages.success(request, 'Thank you for your feedback!')
        else:
            messages.error(request, 'Please provide a rating.')
    
    return redirect('prompts:prompt_detail', slug=slug)

def category_list(request):
    """Display list of categories"""
    categories = Category.objects.annotate(
        prompt_count=Count('prompts', filter=Q(prompts__is_public=True))
    ).order_by('-prompt_count')
    
    context = {
        'categories': categories,
    }
    return render(request, 'prompts/category_list.html', context)

def category_detail(request, pk):
    """Display prompts in a specific category"""
    category = get_object_or_404(Category, pk=pk)
    prompts = Prompt.objects.filter(category=category, is_public=True)
    
    # Pagination
    paginator = Paginator(prompts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'prompts/category_detail.html', context)

@login_required
def my_prompts(request):
    """Display user's own prompts"""
    prompts = Prompt.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(prompts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'prompts/my_prompts.html', context)

@login_required
def prompt_collections(request):
    """Display user's prompt collections"""
    collections = PromptCollection.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'collections': collections,
    }
    return render(request, 'prompts/collections.html', context)

@login_required
def collection_create(request):
    """Create a new prompt collection"""
    if request.method == 'POST':
        form = PromptCollectionForm(request.POST, user=request.user)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            form.save_m2m()
            messages.success(request, 'Collection created successfully!')
            return redirect('prompts:collection_detail', pk=collection.pk)
    else:
        form = PromptCollectionForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Collection',
    }
    return render(request, 'prompts/collection_form.html', context)

def collection_detail(request, pk):
    """Display a prompt collection"""
    collection = get_object_or_404(PromptCollection, pk=pk)
    
    # Check if user can view this collection
    if not collection.is_public and request.user != collection.owner:
        messages.error(request, "This collection is private.")
        return redirect('prompts:prompt_list')
    
    context = {
        'collection': collection,
    }
    return render(request, 'prompts/collection_detail.html', context)

# Admin views (staff only)
@login_required
def admin_dashboard(request):
    """Admin dashboard for prompt management"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('prompts:prompt_list')
    
    # Statistics
    total_prompts = Prompt.objects.count()
    public_prompts = Prompt.objects.filter(is_public=True).count()
    featured_prompts = Prompt.objects.filter(is_featured=True).count()
    total_categories = Category.objects.count()
    total_tags = Tag.objects.count()
    
    # Recent activity
    recent_prompts = Prompt.objects.order_by('-created_at')[:5]
    recent_usage = PromptUsage.objects.order_by('-created_at')[:10]
    
    context = {
        'total_prompts': total_prompts,
        'public_prompts': public_prompts,
        'featured_prompts': featured_prompts,
        'total_categories': total_categories,
        'total_tags': total_tags,
        'recent_prompts': recent_prompts,
        'recent_usage': recent_usage,
    }
    return render(request, 'prompts/admin_dashboard.html', context)
