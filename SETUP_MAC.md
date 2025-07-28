# Django5Template Setup Guide for Mac

This guide will help you set up the Django5Template project on your Mac.

## Prerequisites

- Python 3.11+ (✅ You have Python 3.11.3)
- Node.js and npm (✅ Already installed)
- Git (✅ Already installed)

## Quick Start

The project is already set up! You can start the development server with:

```bash
./start_dev.sh
```

For mobile testing (iPhone), use:

```bash
./start_mobile_dev.sh
```

Or manually:

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server (local only)
python manage.py runserver

# Start the server (accessible from mobile)
python manage.py runserver 0.0.0.0:8000
```

## What's Already Configured

✅ **Virtual Environment**: Created and activated  
✅ **Python Dependencies**: All packages installed  
✅ **Node.js Dependencies**: Tailwind CSS and DaisyUI installed  
✅ **Database**: SQLite database created and migrated  
✅ **Superuser**: Created (username: `lcharleslaing`)  
✅ **Tailwind CSS**: Built and configured  
✅ **Static Files**: Collected and served  

## Access Your Application

- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
  - Username: `lcharleslaing`
  - Password: (the one you set during setup)

## Mobile Testing

For testing on your iPhone:

1. **Start mobile server**: `./start_mobile_dev.sh`
2. **Your Mac's IP**: 192.168.3.147 (may vary)
3. **Mobile URL**: http://192.168.3.147:8000/
4. **QR Code**: Available on the homepage for easy access

**Requirements**:
- iPhone and Mac must be on the same WiFi network
- Use the QR code on the homepage for instant access

## Project Features

This Django template includes:

- **Authentication System**: User registration, login, logout
- **File Management**: Upload, view, and manage files
- **Image Management**: Upload and manage images
- **Prompt Builder**: AI prompt management system
- **User Profiles**: User profile management
- **Search Functionality**: Full-text search across content
- **Subscription System**: User subscription management
- **Modern UI**: Tailwind CSS with DaisyUI components
- **Responsive Design**: Mobile-friendly interface

## Development Workflow

1. **Start Development**: `./start_dev.sh`
2. **Make Changes**: Edit your code
3. **View Changes**: Refresh your browser
4. **Stop Server**: Press `Ctrl+C` in terminal

## Useful Commands

```bash
# Run migrations
python manage.py migrate

# Create new migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Build Tailwind CSS
python manage.py tailwind install

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

## Troubleshooting

If you encounter issues:

1. **Server won't start**: Check if port 8000 is in use
2. **Static files not loading**: Run `python manage.py collectstatic`
3. **Tailwind styles not updating**: Run `python manage.py tailwind install`
4. **Database errors**: Run `python manage.py migrate`

## Next Steps

1. Explore the admin panel at http://127.0.0.1:8000/admin/
2. Check out the different apps in the project
3. Start customizing the templates and views
4. Add your own models and functionality

Happy coding! 🚀 