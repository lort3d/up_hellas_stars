"""
Django test settings for starwarsrest project.
Overrides settings to disable caching for tests.
"""

from .settings import *

# Disable caching for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Remove cache middleware for tests
MIDDLEWARE = [
    middleware for middleware in MIDDLEWARE 
    if middleware != 'starwarsrest.cache_middleware.RedisCacheMiddleware'
]