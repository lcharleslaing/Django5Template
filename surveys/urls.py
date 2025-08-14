from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Index and lists
    path('', views.index, name='index'),
    path('list/', views.survey_list, name='list'),
    path('invites/', views.my_invites, name='my_invites'),

    # Public survey views
    path('<int:pk>/', views.survey_detail, name='detail'),
    path('<int:survey_pk>/take/', views.survey_response, name='take'),
    path('<int:survey_pk>/take/<str:token>/', views.survey_response, name='take_with_token'),
    path('response/<int:pk>/complete/', views.response_complete, name='response_complete'),

    # Results and exports
    path('results/', views.results_index, name='results'),
    path('<int:pk>/export/<str:format>/', views.export_report, name='export'),
    path('<int:pk>/action-note/', views.action_note, name='action_note'),

    # Admin / Builder
    path('admin/', views.survey_admin_list, name='survey_admin_list'),
    path('admin/create/', views.survey_create, name='survey_create'),
    path('admin/ai/', views.ai_builder, name='ai_builder'),
    path('admin/<int:pk>/edit/', views.survey_edit, name='survey_edit'),
    path('admin/<int:pk>/publish/', views.survey_publish, name='publish'),
    path('admin/<int:pk>/invites/', views.survey_invites, name='survey_invites'),
    path('admin/<int:pk>/reports/', views.survey_reports, name='survey_reports'),

    # HTMX endpoints for dynamic updates
    path('admin/<int:survey_pk>/reorder-sections/', views.reorder_sections, name='reorder_sections'),
    path('admin/<int:section_pk>/reorder-questions/', views.reorder_questions, name='reorder_questions'),

    # API endpoints
    path('api/<int:pk>/', views.survey_api_detail, name='survey_api_detail'),
]
