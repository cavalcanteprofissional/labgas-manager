# Cache utility functions
from flask import current_app, request
import hashlib
import json


def _get_cache():
    cache = current_app.extensions.get("cache")
    if cache:
        return next(iter(cache.values()))
    return None


def make_cache_key(prefix):
    return f"{prefix}{getattr(current_app, '_version', 'v1')}"


def get_list_cache_key(prefix, user_id, page, per_page):
    key = f"{prefix}:{user_id}:{page}:{per_page}"
    return key


def get_cached_or_fetch(cache_key, fetch_func, timeout=300):
    cache = _get_cache()
    if cache is None:
        return fetch_func()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    data = fetch_func()
    cache.set(cache_key, data, timeout=timeout)
    return data


def invalidate_cache(prefix, user_id=None):
    cache = _get_cache()
    if cache is None:
        return
    if user_id:
        cache.delete(f"{prefix}:{user_id}")
    else:
        cache.delete(prefix)


def invalidate_user_caches(user_id):
    for prefix in ["dashboard", "cilindro", "elemento", "leitura", "pressao", "amostra"]:
        invalidate_cache(prefix, user_id)


def dashboard_cache_key(user_id):
    return f"dashboard:{user_id}"


def list_cache_key(prefix, user_id, page, per_page):
    return f"{prefix}:{user_id}:{page}:{per_page}"
