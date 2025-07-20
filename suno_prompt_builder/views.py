from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import SongPrompt


def prompt_builder(request):
    """Main view for the song prompt builder interface."""
    return render(request, 'suno_prompt_builder/prompt_builder.html')


@csrf_exempt
@require_http_methods(["POST"])
def save_prompt(request):
    """Save a new song prompt."""
    try:
        data = json.loads(request.body)
        
        # Convert comma-separated strings to lists for styles
        styles = [style.strip() for style in data.get('styles', '').split(',') if style.strip()]
        excluded_styles = [style.strip() for style in data.get('excluded_styles', '').split(',') if style.strip()]
        
        prompt = SongPrompt.objects.create(
            title=data.get('title', ''),
            lyrics=data.get('lyrics', ''),
            subject=data.get('subject', ''),
            styles=styles,
            excluded_styles=excluded_styles,
            weirdness=int(data.get('weirdness', 50)),
            style_influence=int(data.get('style_influence', 50)),
            is_instrumental=data.get('is_instrumental', False)
        )
        
        return JsonResponse({
            'success': True,
            'id': prompt.id,
            'formatted_prompt': prompt.formatted_prompt()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def get_prompts(request):
    """Get all saved prompts."""
    prompts = SongPrompt.objects.all()
    return JsonResponse({
        'prompts': [prompt.formatted_prompt() for prompt in prompts]
    })