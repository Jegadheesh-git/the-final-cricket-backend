# backend/core/querysets.py

def active_only(qs):
    return qs.filter(is_active=True)

def search_by_name(qs, term):
    return qs.filter(name__icontains=term)
