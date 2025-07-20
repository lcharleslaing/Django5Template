from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    PasswordCategory, PasswordEntry, PasswordShare, PasswordFolder,
    UserProfile, SecurityLog, PasswordGenerator, ImportExportLog
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class PasswordCategorySerializer(serializers.ModelSerializer):
    entry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordCategory
        fields = [
            'id', 'name', 'description', 'color', 'icon', 'user',
            'entry_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'entry_count']
    
    def get_entry_count(self, obj):
        return obj.entries.count()


class PasswordFolderSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordFolder
        fields = [
            'id', 'name', 'parent', 'user', 'full_path',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'full_path']
    
    def get_full_path(self, obj):
        return obj.get_full_path()


class PasswordEntrySerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    decrypted_password = serializers.SerializerMethodField()
    shared_with_users = UserSerializer(source='shared_with', many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordEntry
        fields = [
            'id', 'title', 'username', 'email', 'password', 'decrypted_password',
            'website_url', 'notes', 'category', 'category_name', 'user',
            'password_strength', 'last_used', 'password_changed_at',
            'expires_at', 'days_until_expiry', 'is_expired', 'is_favorite',
            'requires_2fa', 'is_shared', 'shared_with_users', 'tags',
            'custom_fields', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'password_strength', 'password_changed_at',
            'created_at', 'updated_at', 'decrypted_password', 'shared_with_users',
            'category_name', 'days_until_expiry', 'is_expired'
        ]
        extra_kwargs = {
            'encrypted_password': {'write_only': True}
        }
    
    def get_decrypted_password(self, obj):
        # Only return decrypted password if user has permission
        request = self.context.get('request')
        if request and request.user == obj.user:
            return obj.get_password()
        return None
    
    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry()
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = super().create(validated_data)
        if password:
            instance.set_password(password)
            instance.password_strength = instance.check_password_strength(password)
            instance.save()
        return instance
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.password_strength = instance.check_password_strength(password)
            instance.save()
        return instance


class PasswordShareSerializer(serializers.ModelSerializer):
    shared_by_username = serializers.CharField(source='shared_by.username', read_only=True)
    shared_with_username = serializers.CharField(source='shared_with.username', read_only=True)
    password_entry_title = serializers.CharField(source='password_entry.title', read_only=True)
    
    class Meta:
        model = PasswordShare
        fields = [
            'id', 'password_entry', 'password_entry_title', 'shared_by',
            'shared_by_username', 'shared_with', 'shared_with_username',
            'permission_level', 'shared_at', 'expires_at', 'is_active'
        ]
        read_only_fields = [
            'id', 'shared_at', 'shared_by_username', 'shared_with_username',
            'password_entry_title'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'two_factor_enabled', 'backup_codes',
            'default_password_length', 'include_uppercase', 'include_lowercase',
            'include_numbers', 'include_symbols', 'exclude_ambiguous',
            'session_timeout', 'auto_lock_enabled', 'password_expiry_notifications',
            'weak_password_alerts', 'login_notifications', 'theme',
            'items_per_page', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'backup_codes', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'totp_secret': {'write_only': True}
        }


class SecurityLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = SecurityLog
        fields = [
            'id', 'user', 'user_username', 'action', 'action_display',
            'resource_type', 'resource_id', 'details', 'ip_address',
            'user_agent', 'timestamp', 'success'
        ]
        read_only_fields = '__all__'


class PasswordGeneratorSerializer(serializers.ModelSerializer):
    generated_password = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordGenerator
        fields = [
            'id', 'name', 'user', 'length', 'include_uppercase',
            'include_lowercase', 'include_numbers', 'include_symbols',
            'exclude_ambiguous', 'custom_symbols', 'exclude_chars',
            'generated_password', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'generated_password']
    
    def get_generated_password(self, obj):
        return obj.generate_password()


class ImportExportLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    operation_display = serializers.CharField(source='get_operation_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ImportExportLog
        fields = [
            'id', 'user', 'user_username', 'operation', 'operation_display',
            'format', 'format_display', 'file_name', 'records_processed',
            'records_successful', 'records_failed', 'success_rate',
            'error_details', 'timestamp', 'success'
        ]
        read_only_fields = '__all__'
    
    def get_success_rate(self, obj):
        if obj.records_processed > 0:
            return round((obj.records_successful / obj.records_processed) * 100, 2)
        return 0


# Additional serializers for specific use cases

class PasswordEntryListSerializer(PasswordEntrySerializer):
    """Simplified serializer for list views without sensitive data"""
    class Meta(PasswordEntrySerializer.Meta):
        fields = [
            'id', 'title', 'username', 'email', 'website_url',
            'category', 'category_name', 'password_strength',
            'last_used', 'expires_at', 'days_until_expiry',
            'is_expired', 'is_favorite', 'is_shared', 'tags',
            'created_at', 'updated_at'
        ]


class PasswordStrengthSerializer(serializers.Serializer):
    """Serializer for password strength checking"""
    password = serializers.CharField()
    strength = serializers.CharField(read_only=True)
    score = serializers.IntegerField(read_only=True)
    suggestions = serializers.ListField(read_only=True)


class PasswordGenerateSerializer(serializers.Serializer):
    """Serializer for password generation"""
    length = serializers.IntegerField(min_value=8, max_value=128, default=16)
    include_uppercase = serializers.BooleanField(default=True)
    include_lowercase = serializers.BooleanField(default=True)
    include_numbers = serializers.BooleanField(default=True)
    include_symbols = serializers.BooleanField(default=True)
    exclude_ambiguous = serializers.BooleanField(default=True)
    custom_symbols = serializers.CharField(required=False, allow_blank=True)
    exclude_chars = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(read_only=True)


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for 2FA setup"""
    qr_code = serializers.CharField(read_only=True)
    secret = serializers.CharField(read_only=True)
    backup_codes = serializers.ListField(read_only=True)


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for 2FA verification"""
    token = serializers.CharField(max_length=6, min_length=6)
    verified = serializers.BooleanField(read_only=True)