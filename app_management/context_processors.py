from .services import AppVisibilityService


def app_visibility(request):
    """Context processor to add app visibility information to all templates"""
    if not request.user.is_authenticated:
        return {
            'visible_apps': [],
            'user_subscription': None,
            'app_visibility_service': None,
        }
    
    service = AppVisibilityService(request.user)
    
    return {
        'visible_apps': service.get_visible_apps(),
        'user_subscription': service.get_user_subscription_info(),
        'app_visibility_service': service,
    }
