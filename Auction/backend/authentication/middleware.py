from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT', 5)  # 5 attempts
        self.block_duration = getattr(settings, 'BLOCK_DURATION', 3600)  # 1 hour
        self.window_size = getattr(settings, 'RATE_LIMIT_WINDOW', 300)  # 5 minutes

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        path = request.path

        # Skip rate limiting for certain paths
        if path in getattr(settings, 'RATE_LIMIT_EXEMPT_PATHS', []):
            return self.get_response(request)

        # Check if IP is blocked
        if self._is_ip_blocked(ip):
            logger.warning(f"Blocked IP {ip} attempted access")
            return JsonResponse({
                'error': 'IP blocked due to too many failed attempts',
                'retry_after': self._get_block_remaining_time(ip)
            }, status=429)

        # Apply rate limiting
        key = f'rate_limit:{ip}:{path}'
        current = cache.get(key, 0)

        if current >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for IP {ip} on path {path}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'retry_after': self._get_rate_limit_remaining_time(key)
            }, status=429)

        response = self.get_response(request)

        # Increment counter for failed attempts
        if response.status_code in [401, 403]:
            cache.incr(key)
            cache.expire(key, self.window_size)

            # Check if we should block the IP
            if current + 1 >= self.rate_limit:
                self._block_ip(ip)

        return response

    def _is_ip_blocked(self, ip):
        return cache.get(f'ip_block:{ip}') is not None

    def _block_ip(self, ip):
        cache.set(f'ip_block:{ip}', True, self.block_duration)
        logger.warning(f"IP {ip} blocked for {self.block_duration} seconds")

    def _get_block_remaining_time(self, ip):
        ttl = cache.ttl(f'ip_block:{ip}')
        return max(0, ttl) if ttl is not None else 0

    def _get_rate_limit_remaining_time(self, key):
        ttl = cache.ttl(key)
        return max(0, ttl) if ttl is not None else 0

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google-analytics.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://www.google-analytics.com; "
            "connect-src 'self' https://www.google-analytics.com;"
        )
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), payment=()'
        )

        return response

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request')

    def __call__(self, request):
        # Log request
        self.logger.info(
            f"Request: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}",
            extra={
                'method': request.method,
                'path': request.path,
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'user': request.user.id if request.user.is_authenticated else None
            }
        )

        response = self.get_response(request)

        # Log response
        self.logger.info(
            f"Response: {response.status_code} for {request.method} {request.path}",
            extra={
                'status_code': response.status_code,
                'method': request.method,
                'path': request.path
            }
        )

        return response 