from django.urls import path
from . import views

app_name = 'prompts'

urlpatterns = [
    # Test view
    path('test/', views.test_view, name='test'),

    # Main prompt views
    path('', views.prompt_list, name='prompt_list'),
    path('create/', views.prompt_create, name='prompt_create'),

    # User-specific views (must come before slug patterns)
    path('my-prompts/', views.my_prompts, name='my_prompts'),
    path('collections/', views.prompt_collections, name='collections'),
    path('collections/create/', views.collection_create, name='collection_create'),
    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),

    # Category views
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),

    # Tag views
    path('tags/<int:pk>/', views.tag_detail, name='tag_detail'),

    # Admin views
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Prompt detail views (must come last to avoid catching other paths)
    path('<slug:slug>/', views.prompt_detail, name='prompt_detail'),
    path('<slug:slug>/edit/', views.prompt_edit, name='prompt_edit'),
    path('<slug:slug>/delete/', views.prompt_delete, name='prompt_delete'),
    path('<slug:slug>/test/', views.prompt_test, name='prompt_test'),
    path('<slug:slug>/rate/', views.prompt_rate, name='prompt_rate'),
]