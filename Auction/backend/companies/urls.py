from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet,
    CompanyAddressViewSet,
    CompanyDocumentViewSet,
    CompanyVerificationView,
    CompanyManagerViewSet,
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'addresses', CompanyAddressViewSet, basename='company-address')
router.register(r'documents', CompanyDocumentViewSet, basename='company-document')
router.register(r'managers', CompanyManagerViewSet, basename='company-manager')

urlpatterns = [
    path('verify/<int:pk>/', CompanyVerificationView.as_view({'get': 'retrieve', 'post': 'create'}), name='company-verification'),
] + router.urls
