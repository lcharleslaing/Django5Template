"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# Import Django's built-in authentication views
from django.contrib.auth import views as auth_views  # Added for authentication views
# Import custom views from main app
from main.views import register, home  # Added for custom home and register views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Home page
    path('', home, name='home'),  # Main landing page
    # Registration page
    path('register/', register, name='register'),  # User registration
    # Login page using Django's built-in view
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # User login
    # Logout page using Django's built-in view
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),  # User logout
    # Password reset views
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),  # Request password reset
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),  # Password reset email sent
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),  # Password reset link
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),  # Password reset complete
]
