from .base import *

# Test settings
DEBUG = False
TESTING = True

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable email sending
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable external services
ONFIDO_API_TOKEN = 'test_token'
STRIPE_API_KEY = 'test_key'
BRAINTREE_MERCHANT_ID = 'test_merchant'
BRAINTREE_PUBLIC_KEY = 'test_public'
BRAINTREE_PRIVATE_KEY = 'test_private'
MPESA_CONSUMER_KEY = 'test_key'
MPESA_CONSUMER_SECRET = 'test_secret'
AGORA_APP_ID = 'test_id'
AGORA_APP_CERTIFICATE = 'test_cert'

# Disable rate limiting
RATELIMIT_ENABLE = False

# Disable security features for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False 