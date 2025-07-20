from django.urls import path
from . import views

app_name = 'suno_prompt_builder'

urlpatterns = [
    path('', views.prompt_builder, name='prompt_builder'),
    path('save/', views.save_prompt, name='save_prompt'),
    path('prompts/', views.get_prompts, name='get_prompts'),
]