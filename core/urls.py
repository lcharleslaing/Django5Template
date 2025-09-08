from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from main.views import register, home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    # File and Image management
    path('files/', include('files.urls')),
    path('images/', include('images.urls')),
    # User Profile management
    path('profile/', include('userprofile.urls')),
    # Prompt management
    path('prompts/', include('prompts.urls')),
    # Suno Prompt Builder
    path('suno-prompt-builder/', include('suno_prompt_builder.urls')),
    # Subscription management
    path('subscriptions/', include('subscriptions.urls')),
    # Search functionality
    path('search/', include('search.urls')),
    # Surveys functionality
    path('surveys/', include(('surveys.urls', 'surveys'), namespace='surveys')),
    # Equipment BOM functionality
    path('equipment/', include('equipment_bom.urls')),
    # App Management functionality
    path('app-management/', include('app_management.urls')),
    # Flow Builder functionality
    path('flow-builder/', include('flow_builder.urls')),
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

# Static and Media files
from django.conf.urls.static import static
from django.views.static import serve

# Serve static files from STATIC_ROOT (production-ready)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media files (for development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
