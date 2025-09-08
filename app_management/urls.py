from django.urls import path
from . import views

app_name = 'app_management'

urlpatterns = [
    path('subscription/', views.subscription_dashboard, name='subscription_dashboard'),
    path('plans/', views.available_plans, name='available_plans'),
    path('assign/<int:user_id>/', views.assign_subscription, name='assign_subscription'),
]
