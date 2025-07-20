from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

import secrets
import string
import pyotp
import qrcode
import io
import base64
import json

from .models import (
    PasswordCategory, PasswordEntry, PasswordShare, PasswordFolder,
    UserProfile, SecurityLog, PasswordGenerator, ImportExportLog
)
from .serializers import (
    PasswordCategorySerializer, PasswordEntrySerializer, PasswordEntryListSerializer,
    PasswordShareSerializer, PasswordFolderSerializer, UserProfileSerializer,
    SecurityLogSerializer, PasswordGeneratorSerializer, ImportExportLogSerializer,
    PasswordStrengthSerializer, PasswordGenerateSerializer, TwoFactorSetupSerializer,
    TwoFactorVerifySerializer, UserSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PasswordCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return PasswordCategory.objects.filter(user=self.request.user).annotate(
            entry_count=Count('entries')
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        self._log_action('password_created', 'PasswordCategory', serializer.instance.id)
    
    def perform_update(self, serializer):
        serializer.save()
        self._log_action('password_updated', 'PasswordCategory', serializer.instance.id)
    
    def perform_destroy(self, instance):
        self._log_action('password_deleted', 'PasswordCategory', instance.id)
        instance.delete()
    
    def _log_action(self, action, resource_type, resource_id):
        SecurityLog.objects.create(
            user=self.request.user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class PasswordFolderViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordFolderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return PasswordFolder.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PasswordEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PasswordEntryListSerializer
        return PasswordEntrySerializer
    
    def get_queryset(self):
        queryset = PasswordEntry.objects.filter(
            Q(user=self.request.user) | 
            Q(shared_with=self.request.user, passwordshare__is_active=True)
        ).distinct()
        
        # Filtering
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(website_url__icontains=search)
            )
        
        favorites = self.request.query_params.get('favorites')
        if favorites == 'true':
            queryset = queryset.filter(is_favorite=True)
        
        expired = self.request.query_params.get('expired')
        if expired == 'true':
            queryset = queryset.filter(expires_at__lt=timezone.now())
        
        weak = self.request.query_params.get('weak')
        if weak == 'true':
            queryset = queryset.filter(password_strength__in=['very_weak', 'weak'])
        
        return queryset.order_by('-updated_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        self._log_action('password_created', 'PasswordEntry', serializer.instance.id)
    
    def perform_update(self, serializer):
        serializer.save()
        self._log_action('password_updated', 'PasswordEntry', serializer.instance.id)
    
    def perform_destroy(self, instance):
        self._log_action('password_deleted', 'PasswordEntry', instance.id)
        instance.delete()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Log password access
        self._log_action('password_viewed', 'PasswordEntry', instance.id)
        # Update last used timestamp
        instance.last_used = timezone.now()
        instance.save(update_fields=['last_used'])
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        entry = self.get_object()
        entry.is_favorite = not entry.is_favorite
        entry.save()
        return Response({'is_favorite': entry.is_favorite})
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        entry = self.get_object()
        username = request.data.get('username')
        permission_level = request.data.get('permission_level', 'view')
        
        try:
            user_to_share = User.objects.get(username=username)
            share, created = PasswordShare.objects.get_or_create(
                password_entry=entry,
                shared_by=request.user,
                shared_with=user_to_share,
                defaults={'permission_level': permission_level}
            )
            
            if not created:
                share.permission_level = permission_level
                share.is_active = True
                share.save()
            
            entry.is_shared = True
            entry.save()
            
            self._log_action('password_shared', 'PasswordEntry', entry.id, {
                'shared_with': username,
                'permission_level': permission_level
            })
            
            return Response({'message': 'Password shared successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        user_entries = PasswordEntry.objects.filter(user=request.user)
        
        stats = {
            'total_passwords': user_entries.count(),
            'weak_passwords': user_entries.filter(
                password_strength__in=['very_weak', 'weak']
            ).count(),
            'expired_passwords': user_entries.filter(
                expires_at__lt=timezone.now()
            ).count(),
            'favorites': user_entries.filter(is_favorite=True).count(),
            'shared': user_entries.filter(is_shared=True).count(),
            'categories': PasswordCategory.objects.filter(user=request.user).count(),
            'recent_activity': SecurityLog.objects.filter(
                user=request.user
            ).order_by('-timestamp')[:5]
        }
        
        return Response(stats)
    
    def _log_action(self, action, resource_type, resource_id, details=None):
        SecurityLog.objects.create(
            user=self.request.user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class PasswordShareViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordShareSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PasswordShare.objects.filter(
            Q(shared_by=self.request.user) | Q(shared_with=self.request.user)
        ).select_related('password_entry', 'shared_by', 'shared_with')


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class SecurityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SecurityLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return SecurityLog.objects.filter(user=self.request.user)


class PasswordGeneratorViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordGeneratorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PasswordGenerator.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PasswordUtilityAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_password(self, request):
        serializer = PasswordGenerateSerializer(data=request.data)
        if serializer.is_valid():
            chars = ""
            
            if serializer.validated_data.get('include_lowercase', True):
                chars += string.ascii_lowercase
            if serializer.validated_data.get('include_uppercase', True):
                chars += string.ascii_uppercase
            if serializer.validated_data.get('include_numbers', True):
                chars += string.digits
            if serializer.validated_data.get('include_symbols', True):
                custom_symbols = serializer.validated_data.get('custom_symbols', '')
                if custom_symbols:
                    chars += custom_symbols
                else:
                    chars += "!@#$%^&*"
            
            if serializer.validated_data.get('exclude_ambiguous', True):
                ambiguous = "0O1lI"
                chars = ''.join(c for c in chars if c not in ambiguous)
            
            exclude_chars = serializer.validated_data.get('exclude_chars', '')
            if exclude_chars:
                chars = ''.join(c for c in chars if c not in exclude_chars)
            
            if not chars:
                chars = string.ascii_letters + string.digits
            
            length = serializer.validated_data.get('length', 16)
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            return Response({'password': password})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_password_strength(self, request):
        serializer = PasswordStrengthSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            
            # Basic strength analysis
            score = 0
            suggestions = []
            length = len(password)
            
            if length >= 8:
                score += 1
            else:
                suggestions.append("Use at least 8 characters")
            
            if length >= 12:
                score += 1
            else:
                suggestions.append("Use at least 12 characters for better security")
            
            if any(c.islower() for c in password):
                score += 1
            else:
                suggestions.append("Include lowercase letters")
            
            if any(c.isupper() for c in password):
                score += 1
            else:
                suggestions.append("Include uppercase letters")
            
            if any(c.isdigit() for c in password):
                score += 1
            else:
                suggestions.append("Include numbers")
            
            if any(c in string.punctuation for c in password):
                score += 1
            else:
                suggestions.append("Include special characters")
            
            if score <= 2:
                strength = 'very_weak'
            elif score <= 3:
                strength = 'weak'
            elif score <= 4:
                strength = 'medium'
            elif score <= 5:
                strength = 'strong'
            else:
                strength = 'very_strong'
            
            return Response({
                'strength': strength,
                'score': score,
                'suggestions': suggestions
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def setup(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if not profile.totp_secret:
            secret = pyotp.random_base32()
            profile.totp_secret = secret
            profile.save()
        else:
            secret = profile.totp_secret
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=request.user.email or request.user.username,
            issuer_name="PWLockdown Password Manager"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = profile.generate_backup_codes()
        profile.save()
        
        return Response({
            'qr_code': f"data:image/png;base64,{qr_code_data}",
            'secret': secret,
            'backup_codes': backup_codes
        })
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            profile = get_object_or_404(UserProfile, user=request.user)
            
            if profile.totp_secret:
                totp = pyotp.TOTP(profile.totp_secret)
                if totp.verify(token, valid_window=1):
                    profile.two_factor_enabled = True
                    profile.save()
                    
                    SecurityLog.objects.create(
                        user=request.user,
                        action='2fa_enabled',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    return Response({'verified': True})
            
            return Response({'verified': False})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def disable(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        profile.two_factor_enabled = False
        profile.totp_secret = ''
        profile.backup_codes = []
        profile.save()
        
        SecurityLog.objects.create(
            user=request.user,
            action='2fa_disabled',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': '2FA disabled successfully'})


# Traditional Django views for the web interface

@login_required
def dashboard(request):
    """Main dashboard view"""
    user_entries = PasswordEntry.objects.filter(user=request.user)
    
    context = {
        'total_passwords': user_entries.count(),
        'weak_passwords': user_entries.filter(
            password_strength__in=['very_weak', 'weak']
        ).count(),
        'expired_passwords': user_entries.filter(
            expires_at__lt=timezone.now()
        ).count(),
        'favorites': user_entries.filter(is_favorite=True).count(),
        'categories': PasswordCategory.objects.filter(user=request.user),
        'recent_passwords': user_entries.order_by('-created_at')[:5],
        'recent_activity': SecurityLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:10]
    }
    
    return render(request, 'pwlockdown/dashboard.html', context)


@login_required
def password_list(request):
    """Password list view"""
    entries = PasswordEntry.objects.filter(user=request.user)
    
    # Apply filters
    category_id = request.GET.get('category')
    if category_id:
        entries = entries.filter(category_id=category_id)
    
    search = request.GET.get('search')
    if search:
        entries = entries.filter(
            Q(title__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    entries = entries.order_by('-updated_at')
    
    context = {
        'entries': entries,
        'categories': PasswordCategory.objects.filter(user=request.user),
        'search_query': search,
        'selected_category': category_id
    }
    
    return render(request, 'pwlockdown/password_list.html', context)


@login_required
def password_generator(request):
    """Password generator view"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    templates = PasswordGenerator.objects.filter(user=request.user)
    
    context = {
        'user_profile': user_profile,
        'templates': templates
    }
    
    return render(request, 'pwlockdown/password_generator.html', context)


@login_required
def security_settings(request):
    """Security settings view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    recent_logs = SecurityLog.objects.filter(user=request.user).order_by('-timestamp')[:20]
    
    context = {
        'profile': profile,
        'recent_logs': recent_logs
    }
    
    return render(request, 'pwlockdown/security_settings.html', context)
