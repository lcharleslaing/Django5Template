from django.urls import path
from .views import site_search

urlpatterns = [
    path('', site_search, name='site_search'),
]