from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from .models import Subscription
from .forms import SubscriptionForm

class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscriptions = context['subscriptions']

        # Calculate totals
        context['total_monthly'] = subscriptions.filter(is_active=True).aggregate(
            total=Sum('amount')
        )['total'] or 0

        context['active_count'] = subscriptions.filter(is_active=True).count()
        context['api_enabled_count'] = subscriptions.filter(is_active=True, is_api_enabled=True).count()

        return context

class SubscriptionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Subscription
    template_name = 'subscriptions/subscription_detail.html'
    context_object_name = 'subscription'

    def test_func(self):
        subscription = self.get_object()
        return subscription.user == self.request.user

class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/subscription_form.html'
    success_url = reverse_lazy('subscriptions:subscription_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Subscription created successfully!')
        return super().form_valid(form)

class SubscriptionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/subscription_form.html'
    success_url = reverse_lazy('subscriptions:subscription_list')

    def test_func(self):
        subscription = self.get_object()
        return subscription.user == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Subscription updated successfully!')
        return super().form_valid(form)

class SubscriptionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Subscription
    template_name = 'subscriptions/subscription_confirm_delete.html'
    success_url = reverse_lazy('subscriptions:subscription_list')

    def test_func(self):
        subscription = self.get_object()
        return subscription.user == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Subscription deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def subscription_dashboard(request):
    """Dashboard view showing subscription statistics"""
    subscriptions = Subscription.objects.filter(user=request.user)

    context = {
        'total_subscriptions': subscriptions.count(),
        'active_subscriptions': subscriptions.filter(is_active=True).count(),
        'api_enabled_subscriptions': subscriptions.filter(is_active=True, is_api_enabled=True).count(),
        'total_monthly_cost': subscriptions.filter(is_active=True).aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'recent_subscriptions': subscriptions.order_by('-created_at')[:5],
        'upcoming_renewals': subscriptions.filter(
            is_active=True
        ).order_by('next_due_date')[:5],
    }

    return render(request, 'subscriptions/subscription_dashboard.html', context)
