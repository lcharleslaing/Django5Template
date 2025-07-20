from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import secrets
import string
import json
from django.core.validators import MinLengthValidator


class PasswordCategory(models.Model):
    """Categories for organizing password entries"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    icon = models.CharField(max_length=50, default='fa-folder')  # FontAwesome icon class
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Password Categories"
        unique_together = ['name', 'user']
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PasswordEntry(models.Model):
    """Main password entry model with encryption"""
    STRENGTH_CHOICES = [
        ('very_weak', 'Very Weak'),
        ('weak', 'Weak'),
        ('medium', 'Medium'),
        ('strong', 'Strong'),
        ('very_strong', 'Very Strong'),
    ]

    title = models.CharField(max_length=200)
    username = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    encrypted_password = models.TextField()  # Encrypted password
    website_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    category = models.ForeignKey(PasswordCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_entries')
    
    # Security features
    password_strength = models.CharField(max_length=12, choices=STRENGTH_CHOICES, default='medium')
    last_used = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    requires_2fa = models.BooleanField(default=False)
    
    # Sharing and collaboration
    is_shared = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        User, 
        through='PasswordShare', 
        through_fields=('password_entry', 'shared_with'),
        related_name='shared_passwords', 
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.JSONField(default=list, blank=True)  # Store tags as JSON array
    custom_fields = models.JSONField(default=dict, blank=True)  # Store custom fields as JSON

    class Meta:
        verbose_name_plural = "Password Entries"
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def set_password(self, raw_password):
        """Encrypt and store password"""
        key = settings.PWLOCKDOWN_ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
        f = Fernet(Fernet.generate_key())
        self.encrypted_password = f.encrypt(raw_password.encode()).decode()
        
    def get_password(self):
        """Decrypt and return password"""
        try:
            key = settings.PWLOCKDOWN_ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
            f = Fernet(Fernet.generate_key())
            return f.decrypt(self.encrypted_password.encode()).decode()
        except:
            return None

    def check_password_strength(self, password):
        """Analyze password strength"""
        score = 0
        length = len(password)
        
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 1
        
        if score <= 2:
            return 'very_weak'
        elif score <= 3:
            return 'weak'
        elif score <= 4:
            return 'medium'
        elif score <= 5:
            return 'strong'
        else:
            return 'very_strong'

    def is_expired(self):
        """Check if password has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def days_until_expiry(self):
        """Get days until password expires"""
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(0, delta.days)
        return None


class PasswordShare(models.Model):
    """Through model for password sharing"""
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'Edit'),
        ('admin', 'Admin'),
    ]

    password_entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_passwords_by')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_passwords_with')
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['password_entry', 'shared_with']

    def __str__(self):
        return f"{self.shared_by.username} shared {self.password_entry.title} with {self.shared_with.username}"


class PasswordFolder(models.Model):
    """Hierarchical folder structure for better organization"""
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'parent', 'user']
        ordering = ['name']

    def __str__(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return f"{self.user.username} - {' / '.join(path)}"

    def get_full_path(self):
        """Get the full folder path"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' / '.join(path)


class UserProfile(models.Model):
    """Extended user profile for password manager settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pwlockdown_profile')
    
    # Security settings
    two_factor_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=100, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Password preferences
    default_password_length = models.IntegerField(default=16)
    include_uppercase = models.BooleanField(default=True)
    include_lowercase = models.BooleanField(default=True)
    include_numbers = models.BooleanField(default=True)
    include_symbols = models.BooleanField(default=True)
    exclude_ambiguous = models.BooleanField(default=True)
    
    # Session settings
    session_timeout = models.IntegerField(default=1800)  # 30 minutes
    auto_lock_enabled = models.BooleanField(default=True)
    
    # Notification settings
    password_expiry_notifications = models.BooleanField(default=True)
    weak_password_alerts = models.BooleanField(default=True)
    login_notifications = models.BooleanField(default=True)
    
    # UI preferences
    theme = models.CharField(max_length=20, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    items_per_page = models.IntegerField(default=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    def generate_backup_codes(self, count=10):
        """Generate backup codes for 2FA"""
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        self.backup_codes = codes
        return codes


class SecurityLog(models.Model):
    """Audit log for security events"""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_created', 'Password Created'),
        ('password_updated', 'Password Updated'),
        ('password_deleted', 'Password Deleted'),
        ('password_viewed', 'Password Viewed'),
        ('password_shared', 'Password Shared'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('failed_login', 'Failed Login'),
        ('password_exported', 'Password Exported'),
        ('settings_changed', 'Settings Changed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, blank=True)  # e.g., 'PasswordEntry', 'Category'
    resource_id = models.IntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.user.username} - {self.get_action_display()} at {self.timestamp}"


class PasswordGenerator(models.Model):
    """Saved password generation templates"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_templates')
    length = models.IntegerField(default=16, validators=[MinLengthValidator(8)])
    include_uppercase = models.BooleanField(default=True)
    include_lowercase = models.BooleanField(default=True)
    include_numbers = models.BooleanField(default=True)
    include_symbols = models.BooleanField(default=True)
    exclude_ambiguous = models.BooleanField(default=True)
    custom_symbols = models.CharField(max_length=100, blank=True)
    exclude_chars = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'user']
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def generate_password(self):
        """Generate a password based on the template settings"""
        chars = ""
        
        if self.include_lowercase:
            chars += string.ascii_lowercase
        if self.include_uppercase:
            chars += string.ascii_uppercase
        if self.include_numbers:
            chars += string.digits
        if self.include_symbols:
            if self.custom_symbols:
                chars += self.custom_symbols
            else:
                chars += "!@#$%^&*"
        
        if self.exclude_ambiguous:
            # Remove ambiguous characters
            ambiguous = "0O1lI"
            chars = ''.join(c for c in chars if c not in ambiguous)
        
        if self.exclude_chars:
            chars = ''.join(c for c in chars if c not in self.exclude_chars)
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        password = ''.join(secrets.choice(chars) for _ in range(self.length))
        return password


class ImportExportLog(models.Model):
    """Log for import/export operations"""
    OPERATION_CHOICES = [
        ('import', 'Import'),
        ('export', 'Export'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('lastpass', 'LastPass'),
        ('bitwarden', 'Bitwarden'),
        ('1password', '1Password'),
        ('chrome', 'Chrome'),
        ('firefox', 'Firefox'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_export_logs')
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    file_name = models.CharField(max_length=255)
    records_processed = models.IntegerField(default=0)
    records_successful = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_details = models.JSONField(default=list, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_operation_display()} {self.get_format_display()} at {self.timestamp}"
