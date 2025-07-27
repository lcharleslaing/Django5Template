from django.urls import path, include
from main.views import home, search_api
from django.shortcuts import render

urlpatterns = [
    path('', home, name='home'),
    path('api/search/', search_api, name='search_api'),
    path('test-search/', lambda request: render(request, 'main/test_search.html'), name='test_search'),
]
