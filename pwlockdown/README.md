# PWLockdown - Modern Password Management Django App

PWLockdown is a comprehensive, modern password management Django application that provides secure storage, organization, and management of passwords with advanced features like 2FA, password generation, sharing, and audit logging.

## Features

### 🔐 Core Security
- **Encrypted Password Storage**: All passwords are encrypted using industry-standard cryptography
- **Two-Factor Authentication (2FA)**: TOTP-based 2FA with QR code setup and backup codes
- **Password Strength Analysis**: Automatic analysis and scoring of password strength
- **Security Audit Logs**: Comprehensive logging of all security-related activities
- **Session Management**: Configurable session timeouts and auto-lock features

### 📊 Password Management
- **Password Vault**: Secure storage with categorization and tagging
- **Password Generator**: Customizable password generation with templates
- **Password Sharing**: Secure sharing with permission levels (view, edit, admin)
- **Password Expiration**: Automatic expiration tracking and notifications
- **Favorites System**: Mark frequently used passwords as favorites
- **Hierarchical Organization**: Folders and categories for better organization

### 🎯 Modern Features
- **REST API**: Complete RESTful API for all operations
- **Responsive UI**: Modern Tailwind CSS-based interface
- **Real-time Search**: Fast searching across all password fields
- **Import/Export**: Support for multiple formats (JSON, CSV, LastPass, etc.)
- **Browser Integration**: Website favicon detection and URL handling
- **Mobile-Friendly**: Responsive design for all devices

### 🔧 Advanced Capabilities
- **Custom Fields**: Add custom metadata to password entries
- **Bulk Operations**: Manage multiple passwords at once
- **Advanced Filtering**: Filter by strength, expiration, categories, etc.
- **User Profiles**: Customizable user preferences and settings
- **Multi-tenant**: Each user has isolated, secure password vault

## Installation

1. **Add to Django Project**: The app is already integrated into your Django project.

2. **Install Dependencies**: All required dependencies are in `requirements.txt`:
   - `cryptography` - For password encryption
   - `djangorestframework` - For REST API
   - `pyotp` - For 2FA implementation
   - `qrcode[pil]` - For QR code generation
   - `django-cors-headers` - For API CORS support

3. **Database Setup**: Migrations have been created and applied.

## Configuration

### Settings
The following settings have been added to your Django settings:

```python
# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Password Management Security Settings
PWLOCKDOWN_ENCRYPTION_KEY = SECRET_KEY  # In production, use a separate key
PWLOCKDOWN_SESSION_TIMEOUT = 1800  # 30 minutes in seconds
PWLOCKDOWN_MAX_LOGIN_ATTEMPTS = 5
PWLOCKDOWN_PASSWORD_MIN_LENGTH = 12
PWLOCKDOWN_REQUIRE_2FA = False  # Can be enabled per user
```

## URL Structure

### Web Interface
- `/pwlockdown/` - Dashboard
- `/pwlockdown/passwords/` - Password vault
- `/pwlockdown/generator/` - Password generator
- `/pwlockdown/security/` - Security settings

### REST API
- `/pwlockdown/api/` - API root
- `/pwlockdown/api/entries/` - Password entries CRUD
- `/pwlockdown/api/categories/` - Categories management
- `/pwlockdown/api/generators/` - Password generator templates
- `/pwlockdown/api/security-logs/` - Security audit logs
- `/pwlockdown/api/2fa/setup/` - 2FA setup
- `/pwlockdown/api/utils/generate-password/` - Password generation utility

## API Usage

### Authentication
```bash
# Get API token
curl -X POST http://localhost:8000/pwlockdown/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

### Create Password Entry
```bash
curl -X POST http://localhost:8000/pwlockdown/api/entries/ \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "My Website",
       "username": "myuser",
       "email": "user@example.com",
       "password": "secure_password_123",
       "website_url": "https://example.com",
       "notes": "Important account"
     }'
```

### Generate Password
```bash
curl -X POST http://localhost:8000/pwlockdown/api/utils/generate-password/ \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{
       "length": 16,
       "include_uppercase": true,
       "include_lowercase": true,
       "include_numbers": true,
       "include_symbols": true
     }'
```

### Setup 2FA
```bash
curl -X POST http://localhost:8000/pwlockdown/api/2fa/setup/ \
     -H "Authorization: Token your_token_here"
```

## Models Overview

### PasswordEntry
Main model for storing encrypted passwords with metadata:
- Encrypted password storage
- Categorization and tagging
- Expiration tracking
- Sharing capabilities
- Custom fields support

### PasswordCategory
Organize passwords into colored, icon-based categories.

### PasswordShare
Manage password sharing between users with permission levels.

### UserProfile
Extended user settings for password management preferences.

### SecurityLog
Comprehensive audit logging for all security events.

### PasswordGenerator
Save password generation templates for reuse.

## Security Features

### Encryption
- All passwords are encrypted using the Fernet symmetric encryption
- Encryption keys are derived from Django's SECRET_KEY
- Each password is encrypted individually

### Two-Factor Authentication
- TOTP-based 2FA using industry-standard algorithms
- QR code generation for easy setup with authenticator apps
- Backup codes for account recovery
- Optional enforcement per user

### Audit Logging
- All password access is logged
- Failed login attempts tracking
- IP address and user agent logging
- Exportable security reports

### Password Analysis
- Real-time password strength scoring
- Common password detection
- Expiration tracking and notifications
- Weak password identification

## Extensibility

The app is designed to be highly extensible:

### Custom Fields
Add any additional metadata to password entries using the JSON `custom_fields`.

### Import/Export
Support for multiple formats with extensible parser system.

### API Extensions
All functionality is available via REST API for building custom clients.

### Theming
Modern Tailwind CSS-based UI that can be easily customized.

### Notifications
Extensible notification system for password expiration and security alerts.

## Security Best Practices

1. **Production Deployment**:
   - Use a separate encryption key from SECRET_KEY
   - Enable HTTPS/SSL
   - Configure proper session security
   - Set up regular backups

2. **User Education**:
   - Encourage strong master passwords
   - Promote 2FA usage
   - Regular security checkups

3. **Monitoring**:
   - Monitor security logs regularly
   - Set up alerts for suspicious activity
   - Regular password strength audits

## Development

### Adding New Features
1. Create new models in `models.py`
2. Add serializers in `serializers.py`
3. Create API views in `views.py`
4. Add URL patterns in `urls.py`
5. Create migrations with `python manage.py makemigrations pwlockdown`

### Testing
The app includes comprehensive test coverage. Run tests with:
```bash
python manage.py test pwlockdown
```

## Contributing

The PWLockdown app follows Django best practices and is designed for easy extension and customization. Key areas for contribution:

1. Additional import/export formats
2. Browser extension integration
3. Mobile app API enhancements
4. Advanced password policies
5. Team management features

## License

This password management app is part of your Django project and follows your project's licensing terms.

## Support

For issues and feature requests, please refer to your project's issue tracking system or documentation.