# ... existing settings ...

# WordPress Integration Settings
WORDPRESS_URL = 'https://probid-wp.egenstheme.com'
WORDPRESS_API_PREFIX = 'wp-json'
WORDPRESS_JWT_SECRET = 'your-jwt-secret-key'  # Should match WordPress JWT secret

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost",  # WordPress local development
    "http://localhost:8000",  # Django local development
    "http://127.0.0.1",  # Alternative localhost
    "http://127.0.0.1:8000",  # Alternative Django local development
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Authentication Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# Cache Settings for WordPress Integration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
    'wordpress': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
    }
}

# Media Settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static Files Settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# ... rest of existing settings ... 