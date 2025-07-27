from django.shortcuts import render
from django.apps import apps
from django.db.models import Q, CharField, TextField
from django.contrib.auth.decorators import login_required

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        for model in apps.get_models():
            try:
                # Skip proxy or abstract models
                if model._meta.abstract or model._meta.proxy:
                    continue

                # Build query on CharFields and TextFields
                fields = [f.name for f in model._meta.fields if isinstance(f, (CharField, TextField))]
                if not fields:
                    continue

                q = Q()
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})

                # Default queryset
                queryset = model.objects.all()

                # Filter to user-owned objects based on ownership field
                field_names = [f.name for f in model._meta.fields]
                if 'user' in field_names:
                    queryset = queryset.filter(user=request.user)
                elif 'uploaded_by' in field_names:
                    queryset = queryset.filter(uploaded_by=request.user)
                elif 'author' in field_names:
                    queryset = queryset.filter(author=request.user)
                elif 'owner' in field_names:
                    queryset = queryset.filter(owner=request.user)

                # Optional: exclude test data if marked
                if 'is_test' in field_names:
                    queryset = queryset.filter(is_test=False)

                found = queryset.filter(q)[:5]
                if found:
                    results.append({
                        'model': model.__name__,
                        'items': found
                    })

            except Exception as e:
                print(f"[SEARCH ERROR] {model.__name__}: {e}")

    # If AJAX (modal search), return partial
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "search/partials/result_list.html", {
            "results": results,
            "query": query,
        })

    # Otherwise full search result page
    return render(request, "search/results.html", {
        "results": results,
        "query": query,
    })
