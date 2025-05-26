from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OAuthViewSet,
    KYCVerificationViewSet,
    SecurityLogViewSet,
    TwoFactorAuthViewSet,
    health_check,
    sync_user
)

router = DefaultRouter()
router.register(r'oauth', OAuthViewSet, basename='oauth')
router.register(r'kyc', KYCVerificationViewSet, basename='kyc')
router.register(r'security-logs', SecurityLogViewSet, basename='security-logs')
router.register(r'2fa', TwoFactorAuthViewSet, basename='2fa')

urlpatterns = [
    path('', include(router.urls)),
    path('oauth/google/', OAuthViewSet.as_view({'post': 'google_login'}), name='google-login'),
    path('kyc/webhook/', KYCVerificationViewSet.as_view({'post': 'webhook'}), name='kyc-webhook'),
    path('health-check/', health_check, name='health-check'),
    path('sync-user/', sync_user, name='sync-user'),
] 