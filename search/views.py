from django.http import JsonResponse
from django.apps import apps
from django.db.models import Q, CharField, TextField
from django.urls import reverse
from django.contrib.admin.utils import quote


MAX_RESULTS = 50  # Limit to avoid excessive data transfer


def _model_search_queryset(model, query):
    """Return queryset for a model that matches the query on any Char/Text field."""
    # Build dynamic OR query across all char/text fields
    search_fields = [
        f.name for f in model._meta.get_fields()
        if isinstance(f, (CharField, TextField))
    ]
    if not search_fields:
        return model.objects.none()

    filters = Q()
    for field in search_fields:
        filters |= Q(**{f"{field}__icontains": query})
    return model.objects.filter(filters)


def _object_to_result(obj):
    """Convert model instance to serialisable search result dict."""
    model = obj._meta
    # Prefer get_absolute_url if implemented, fallback to admin change page
    try:
        url = obj.get_absolute_url()
    except Exception:
        try:
            url = reverse(f"admin:{model.app_label}_{model.model_name}_change", args=[quote(obj.pk)])
        except Exception:
            url = "#"

    return {
        "title": str(obj),
        "subtitle": f"{model.verbose_name.title()} (ID: {obj.pk})",  # e.g. "User (ID: 1)"
        "url": url,
    }


def site_search(request):
    """Return JSON response containing site-wide search results.

    The search iterates over every model in the project and performs an
    icontains query across all CharField and TextField fields, capped to a
    maximum number of overall results for performance. New models added in
    the future are automatically included because we introspect at runtime.
    """
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        for model in apps.get_models():
            # Skip proxy models or those without a manager
            if getattr(model, "_meta", None) and model._meta.proxy:
                continue
            try:
                qs = _model_search_queryset(model, query)[:5]  # limit per model
                results.extend([_object_to_result(obj) for obj in qs])
            except Exception:
                # Some models might not be queryable (e.g. unmanaged). Ignore them.
                continue
            if len(results) >= MAX_RESULTS:
                break

    return JsonResponse({"results": results})