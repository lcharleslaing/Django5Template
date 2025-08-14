from django.utils import timezone
from django.conf import settings


def surveys_context(request):
    data = {
        "SURVEYS_ENABLED": getattr(settings, "SURVEYS_ENABLED", True),
    }
    try:
        user = request.user
        if user.is_authenticated:
            from .models import Invite, Survey
            now = timezone.now()
            data["survey_invites_count"] = Invite.objects.filter(
                email__iexact=user.email, used_at__isnull=True, expires_at__gt=now
            ).count()
            data["open_surveys_count"] = Survey.objects.filter(
                status="PUBLISHED", publish_start__lte=now, publish_end__gte=now
            ).count()
    except Exception:
        data.setdefault("survey_invites_count", 0)
        data.setdefault("open_surveys_count", 0)
    return data


