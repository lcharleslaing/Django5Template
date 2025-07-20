from django.contrib import admin
from django.urls import path, include   
from django.contrib.auth import views as auth_views
from django.conf import settings
from main.views import register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    # File and Image management
    path('files/', include('files.urls')),
    path('images/', include('images.urls')),
    # User Profile management
    path('profile/', include('userprofile.urls')),
    # Prompt management
    path('prompts/', include('prompts.urls')),
    # Global search endpoint
    path('search/', include('search.urls')),
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

# Media files (for development)
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
