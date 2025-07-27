from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionListView.as_view(), name='subscription_list'),
    path('dashboard/', views.subscription_dashboard, name='subscription_dashboard'),
    path('create/', views.SubscriptionCreateView.as_view(), name='subscription_create'),
    path('<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('<int:pk>/update/', views.SubscriptionUpdateView.as_view(), name='subscription_update'),
    path('<int:pk>/delete/', views.SubscriptionDeleteView.as_view(), name='subscription_delete'),
]