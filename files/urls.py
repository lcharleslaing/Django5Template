from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('upload/', views.file_upload, name='file_upload'),
    path('<int:file_id>/', views.file_detail, name='file_detail'),
    path('<int:file_id>/download/', views.file_download, name='file_download'),
    path('<int:file_id>/delete/', views.file_delete, name='file_delete'),
]
