from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import SubscriptionPlan, UserSubscription
from .services import AppVisibilityService


@login_required
def subscription_dashboard(request):
    """Dashboard showing user's subscription and available apps"""
    service = AppVisibilityService(request.user)
    visible_apps = service.get_visible_apps()
    subscription_info = service.get_user_subscription_info()
    
    context = {
        'visible_apps': visible_apps,
        'subscription_info': subscription_info,
        'user_subscription': subscription_info['plan'] if subscription_info else None,
    }
    
    return render(request, 'app_management/subscription_dashboard.html', context)


@login_required
def assign_subscription(request, user_id):
    """Assign a subscription plan to a user (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to assign subscriptions.')
        return redirect('app_management:subscription_dashboard')
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            user = User.objects.get(id=user_id)
            
            # Create or update user subscription
            subscription, created = UserSubscription.objects.get_or_create(
                user=user,
                defaults={'plan': plan}
            )
            
            if not created:
                subscription.plan = plan
                subscription.save()
            
            messages.success(request, f'Successfully assigned {plan.name} plan to {user.username}')
        except (SubscriptionPlan.DoesNotExist, User.DoesNotExist):
            messages.error(request, 'Invalid plan or user selected.')
    
    return redirect('app_management:subscription_dashboard')


@login_required
def available_plans(request):
    """Show available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    context = {
        'plans': plans,
        'current_subscription': None,
    }
    
    if request.user.is_authenticated:
        service = AppVisibilityService(request.user)
        subscription_info = service.get_user_subscription_info()
        if subscription_info:
            context['current_subscription'] = subscription_info['plan']
    
    return render(request, 'app_management/available_plans.html', context)