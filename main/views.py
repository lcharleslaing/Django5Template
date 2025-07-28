from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone

# User registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    # Get dashboard statistics
    stats = get_dashboard_stats(request.user)
    recent_activity = get_recent_activity(request.user)

    # Generate QR code for mobile testing
    import qrcode
    from io import BytesIO
    import base64
    import socket
    
    # Get the current server URL
    protocol = 'https' if request.is_secure() else 'http'
    
    # Get the actual IP address for mobile access
    try:
        # Get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        server_url = f"{protocol}://{local_ip}:8000"
    except:
        # Fallback to request host
        host = request.get_host()
        server_url = f"{protocol}://{host}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(server_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'stats': stats,
        'recent_activity': recent_activity,
        'server_url': server_url,
        'qr_code_image': qr_image_base64,
        'year': datetime.now().year,
        'timestamp': timezone.now().timestamp(),  # For cache busting
    }
    return render(request, 'main/dashboard.html', context)

def home_public(request):
    """Public home page with QR code for mobile testing"""
    import qrcode
    from io import BytesIO
    import base64
    import socket
    
    # Get the current server URL
    protocol = 'https' if request.is_secure() else 'http'
    
    # Get the actual IP address for mobile access
    try:
        # Get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        server_url = f"{protocol}://{local_ip}:8000"
    except:
        # Fallback to request host
        host = request.get_host()
        server_url = f"{protocol}://{host}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(server_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'server_url': server_url,
        'qr_code_image': qr_image_base64,
        'year': datetime.now().year,
    }
    return render(request, 'main/home.html', context)

def get_dashboard_stats(user):
    """Get statistics for all apps and models with user-specific data"""
    stats = []

    try:
        from django.apps import apps
        from django.db.models import Count, Sum
        from django.contrib.auth.models import User

        # Define stat configurations with icons and colors
        stat_configs = {
            'prompts': {
                'label': 'AI Prompts',
                'icon_bg': 'from-blue-500 to-indigo-600',
                'icon_path': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />',
                'model_name': 'prompt',
                'app_label': 'prompts',
                'user_field': 'author'
            },

            'subscriptions': {
                'label': 'Subscriptions',
                'icon_bg': 'from-purple-500 to-pink-600',
                'icon_path': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />',
                'model_name': 'subscription',
                'app_label': 'subscriptions',
                'user_field': 'user'
            },
            'files': {
                'label': 'Files',
                'icon_bg': 'from-orange-500 to-red-600',
                'icon_path': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />',
                'model_name': 'file',
                'app_label': 'files',
                'user_field': 'uploaded_by'
            },
            'images': {
                'label': 'Images',
                'icon_bg': 'from-green-500 to-emerald-600',
                'icon_path': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />',
                'model_name': 'image',
                'app_label': 'images',
                'user_field': 'uploaded_by'
            }
        }

        # Get stats for each configured model
        for key, config in stat_configs.items():
            try:
                model = apps.get_model(config['app_label'], config['model_name'])

                # Get user-specific count
                user_filter = {config['user_field']: user}
                count = model.objects.filter(**user_filter).count()

                # Get new this week count
                week_ago = timezone.now() - timedelta(days=7)
                if hasattr(model, 'created_at'):
                    new_this_week = model.objects.filter(
                        **user_filter,
                        created_at__gte=week_ago
                    ).count()
                elif hasattr(model, 'uploaded_at'):
                    new_this_week = model.objects.filter(
                        **user_filter,
                        uploaded_at__gte=week_ago
                    ).count()
                else:
                    new_this_week = 0

                stats.append({
                    'label': config['label'],
                    'count': count,
                    'new_this_week': new_this_week if new_this_week > 0 else None,
                    'icon_bg': config['icon_bg'],
                    'icon_path': config['icon_path']
                })

            except Exception as e:
                print(f"Error getting stats for {key}: {e}")
                continue

    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        stats = []

    return stats

def get_recent_activity(user):
    """Get recent activity across all models for the specific user"""
    activities = []

    try:
        from django.apps import apps

        # Define models to track for activity
        activity_models = [
            {'app': 'prompts', 'model': 'prompt', 'user_field': 'author'},
            {'app': 'subscriptions', 'model': 'subscription', 'user_field': 'user'},
            {'app': 'files', 'model': 'file', 'user_field': 'uploaded_by'},
            {'app': 'images', 'model': 'image', 'user_field': 'uploaded_by'},
        ]

        for model_config in activity_models:
            try:
                model = apps.get_model(model_config['app'], model_config['model'])
                user_filter = {model_config['user_field']: user}

                # Get recent items for this user
                recent_items = None
                if hasattr(model, 'created_at'):
                    recent_items = model.objects.filter(**user_filter).order_by('-created_at')[:5]
                elif hasattr(model, 'uploaded_at'):
                    recent_items = model.objects.filter(**user_filter).order_by('-uploaded_at')[:5]
                elif hasattr(model, 'updated_at'):
                    recent_items = model.objects.filter(**user_filter).order_by('-updated_at')[:5]

                if recent_items:
                    for item in recent_items:
                        activity_time = None
                        if hasattr(item, 'created_at'):
                            activity_time = item.created_at
                        elif hasattr(item, 'uploaded_at'):
                            activity_time = item.uploaded_at
                        elif hasattr(item, 'updated_at'):
                            activity_time = item.updated_at

                        if activity_time:
                            activities.append({
                                'type': model_config['model'],
                                'app': model_config['app'],
                                'title': str(item),
                                'time': activity_time,
                                'id': item.pk,
                            })
            except Exception as e:
                print(f"Error getting activity for {model_config['app']}.{model_config['model']}: {e}")
                continue

    except Exception as e:
        print(f"Error in get_recent_activity: {e}")
        activities = []

    # Sort by time and return most recent 10
    activities.sort(key=lambda x: x['time'], reverse=True)
    return activities[:10]
