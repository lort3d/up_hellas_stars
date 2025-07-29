import hashlib
import re
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)

class RedisCacheMiddleware(MiddlewareMixin):
    """
    Middleware to cache GET requests for list and retrieve operations using Redis.
    """
    
    # Regex patterns for list and retrieve operations
    LIST_PATTERN = re.compile(r'/api/(characters|films|starships)/')
    RETRIEVE_PATTERN = re.compile(r'/api/(characters|films|starships)/\d+/')
    
    def process_request(self, request):
        # Only cache GET requests for list and retrieve operations
        if request.method != 'GET':
            return None
            
        # Check if this is a list or retrieve operation
        if not (self.LIST_PATTERN.match(request.path) or self.RETRIEVE_PATTERN.match(request.path)):
            return None
            
        # Generate cache key based on path and query parameters
        cache_key = self._generate_cache_key(request)
        
        # Try to get response from cache
        cached_response = cache.get(cache_key)
        logger.info(f"Checking cache for key: {cache_key}")
        if cached_response:
            logger.info(f"Cache HIT for key: {cache_key}")
            print(f"Cache HIT for key: {cache_key}")
            # Return cached response
            return HttpResponse(
                content=cached_response['content'],
                status=cached_response['status'],
                content_type=cached_response['content_type']
            )
        else:
            logger.info(f"Cache MISS for key: {cache_key}")
            print(f"Cache MISS for key: {cache_key}")
        
        # Store cache key in request for later use in process_response
        request._cache_key = cache_key
        return None
    
    def process_response(self, request, response):
        # Only cache GET requests with successful responses for list and retrieve operations
        if (request.method == 'GET' and 
            response.status_code == 200 and 
            hasattr(request, '_cache_key')):
            
            # Check if this is a list or retrieve operation
            if not (self.LIST_PATTERN.match(request.path) or self.RETRIEVE_PATTERN.match(request.path)):
                return response
            
            # Cache the response for 5 minutes (300 seconds)
            cache.set(request._cache_key, {
                'content': response.content.decode('utf-8'),
                'status': response.status_code,
                'content_type': response.get('Content-Type', 'application/json')
            }, 300)  # 5 minutes cache timeout
            logger.info(f"Cached response for key: {request._cache_key}")
            print(f"Cached response for key: {request._cache_key}")
            
        return response
    
    def _generate_cache_key(self, request):
        """
        Generate a unique cache key based on request path and query parameters.
        """
        # Create a string with path and sorted query parameters
        query_params = '&'.join([f"{k}={v}" for k, v in sorted(request.GET.items())])
        key_string = f"{request.path}?{query_params}"
        
        # Hash the key string to create a consistent cache key
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()