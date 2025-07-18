from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('upload/', views.image_upload, name='image_upload'),
    path('<int:image_id>/', views.image_detail, name='image_detail'),
    path('<int:image_id>/delete/', views.image_delete, name='image_delete'),
]
