from django import template
from django.utils import timezone
from django.conf import settings
import datetime

register = template.Library()

@register.simple_tag
def session_expires_in(request):
    """Return how long until the session expires"""
    if not request.user.is_authenticated:
        return None
    
    # Get session expiry time
    expiry = request.session.get_expiry_date()
    if expiry:
        now = timezone.now()
        if expiry > now:
            delta = expiry - now
            days = delta.days
            hours = delta.seconds // 3600
            
            if days > 0:
                return f"{days} day{'s' if days != 1 else ''}"
            elif hours > 0:
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                return "Less than 1 hour"
    
    return "Browser session"

@register.simple_tag
def is_remember_me_enabled(request):
    """Check if remember me is enabled for this session"""
    if not request.user.is_authenticated:
        return False
    
    # Check if session expires at browser close (0) or has a specific time
    expiry = request.session.get_expiry_age()
    return expiry > 0
