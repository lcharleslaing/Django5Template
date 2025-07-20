from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views

# API Router setup
router = DefaultRouter()
router.register(r'categories', views.PasswordCategoryViewSet, basename='passwordcategory')
router.register(r'folders', views.PasswordFolderViewSet, basename='passwordfolder')
router.register(r'entries', views.PasswordEntryViewSet, basename='passwordentry')
router.register(r'shares', views.PasswordShareViewSet, basename='passwordshare')
router.register(r'profile', views.UserProfileViewSet, basename='userprofile')
router.register(r'security-logs', views.SecurityLogViewSet, basename='securitylog')
router.register(r'generators', views.PasswordGeneratorViewSet, basename='passwordgenerator')

app_name = 'pwlockdown'

urlpatterns = [
    # Traditional Django views
    path('', views.dashboard, name='dashboard'),
    path('passwords/', views.password_list, name='password_list'),
    path('generator/', views.password_generator, name='password_generator'),
    path('security/', views.security_settings, name='security_settings'),
    
    # REST API endpoints
    path('api/', include(router.urls)),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Utility API endpoints
    path('api/utils/generate-password/', views.PasswordUtilityAPIView.as_view(), name='api_generate_password'),
    path('api/utils/check-strength/', views.PasswordUtilityAPIView.as_view(), name='api_check_strength'),
    
    # Two-Factor Authentication API endpoints
    path('api/2fa/setup/', views.TwoFactorAPIView.as_view(), name='api_2fa_setup'),
    path('api/2fa/verify/', views.TwoFactorAPIView.as_view(), name='api_2fa_verify'),
    path('api/2fa/disable/', views.TwoFactorAPIView.as_view(), name='api_2fa_disable'),
]