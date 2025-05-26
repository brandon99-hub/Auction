from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
import time

class IPBlockingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.IP_BLOCKING_ENABLED:
            return self.get_response(request)

        ip = self.get_client_ip(request)
        cache_key = f'ip_block:{ip}'
        
        # Check if IP is blocked
        if cache.get(cache_key):
            return HttpResponseForbidden('Too many requests. Please try again later.')

        # Get request count
        request_count = cache.get(f'ip_request_count:{ip}', 0)
        
        # Increment request count
        cache.set(
            f'ip_request_count:{ip}',
            request_count + 1,
            timeout=60  # 1 minute
        )

        # Check if threshold is exceeded
        if request_count + 1 > settings.IP_BLOCKING_THRESHOLD:
            # Block IP
            cache.set(
                cache_key,
                True,
                timeout=settings.IP_BLOCKING_DURATION
            )
            return HttpResponseForbidden('Too many requests. IP blocked.')

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 