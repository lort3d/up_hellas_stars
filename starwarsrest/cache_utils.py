from django.core.cache import cache


def invalidate_cache_for_model(model_name):
    """
    Invalidate cache entries for a specific model.
    This is a placeholder implementation. In a production environment,
    you might want to use a more sophisticated cache tagging system.
    """
    # For now, we'll just clear the entire cache
    # A more advanced implementation might use cache tags
    cache.clear()


def invalidate_all_cache():
    """
    Invalidate all cache entries.
    """
    cache.clear()