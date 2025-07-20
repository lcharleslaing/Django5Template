from django.urls import path, include
from main.views import home, search_api

urlpatterns = [
    path('', home, name='home'),
    path('api/search/', search_api, name='search_api'),
]
