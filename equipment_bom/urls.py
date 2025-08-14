from django.urls import path
from . import views

app_name = 'equipment_bom'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/edit/', views.job_edit, name='job_edit'),
    
    # Equipment
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:equipment_id>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/create/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:equipment_id>/edit/', views.equipment_edit, name='equipment_edit'),
    
    # Materials
    path('materials/', views.material_list, name='material_list'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:material_id>/edit/', views.material_edit, name='material_edit'),
    
    # BOM Templates
    path('templates/', views.bom_template_list, name='bom_template_list'),
    path('templates/<int:template_id>/', views.bom_template_detail, name='bom_template_detail'),
    path('templates/create/', views.bom_template_create, name='bom_template_create'),
    path('templates/<int:template_id>/edit/', views.bom_template_edit, name='bom_template_edit'),
    
    # Import/Export
    path('import/', views.import_excel, name='import_excel'),
    path('import/logs/', views.import_logs, name='import_logs'),
    path('import/logs/<int:log_id>/', views.import_log_detail, name='import_log_detail'),
    path('export/<int:equipment_type_id>/', views.export_excel, name='export_excel'),
    
    # API endpoints
    path('api/equipment-data/', views.api_equipment_data, name='api_equipment_data'),
]
