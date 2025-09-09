from django.urls import path
from . import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.profile_view, name='profile_view'),
    path('edit/', views.profile_edit, name='profile_edit'),
    path('password/', views.password_change, name='password_change'),
    path('list/', views.profile_list, name='profile_list'),
    path('avatar/remove/', views.avatar_remove, name='avatar_remove'),
    path('<str:username>/', views.profile_view, name='profile_view'),
] 