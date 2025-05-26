from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Company, CompanyAddress, CompanyDocument
from .serializers import (
    CompanySerializer,
    CompanyAddressSerializer,
    CompanyDocumentSerializer,
    CompanyVerificationSerializer,
    CompanyManagerSerializer,
)
from users.models import User
from django.db import transaction

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        verified = self.request.query_params.get('verified', None)
        search = self.request.query_params.get('search', None)

        if status:
            queryset = queryset.filter(status=status)
        if verified:
            queryset = queryset.filter(verified=verified.lower() == 'true')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def perform_create(self, serializer):
        company = serializer.save()
        company.managers.add(self.request.user)

    @action(detail=True, methods=['post'])
    def request_verification(self, request, pk=None):
        company = self.get_object()
        if not company.managers.filter(pk=request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        
        company.status = Company.Status.PENDING
        company.save()
        return Response({'status': 'Verification requested'})

class CompanyAddressViewSet(viewsets.ModelViewSet):
    queryset = CompanyAddress.objects.all()
    serializer_class = CompanyAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.query_params.get('company', None)
        is_primary = self.request.query_params.get('is_primary', None)

        if company:
            queryset = queryset.filter(company_id=company)
        if is_primary:
            queryset = queryset.filter(is_primary=is_primary.lower() == 'true')
        return queryset

    def perform_create(self, serializer):
        company = get_object_or_404(Company, pk=self.request.data.get('company'))
        if not company.managers.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        serializer.save()

    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        address = self.get_object()
        if not address.company.managers.filter(pk=request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        
        with transaction.atomic():
            CompanyAddress.objects.filter(company=address.company).update(is_primary=False)
            address.is_primary = True
            address.save()
        
        return Response({'status': 'Primary address set'})

class CompanyDocumentViewSet(viewsets.ModelViewSet):
    queryset = CompanyDocument.objects.all()
    serializer_class = CompanyDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.query_params.get('company', None)
        document_type = self.request.query_params.get('document_type', None)
        verified = self.request.query_params.get('verified', None)

        if company:
            queryset = queryset.filter(company_id=company)
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        if verified:
            queryset = queryset.filter(verified=verified.lower() == 'true')
        return queryset

    def perform_create(self, serializer):
        company = get_object_or_404(Company, pk=self.request.data.get('company'))
        if not company.managers.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        serializer.save()

class CompanyVerificationView(viewsets.GenericViewSet):
    serializer_class = CompanyVerificationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk=None):
        company = get_object_or_404(Company, pk=pk)
        if not request.user.is_staff:
            raise PermissionDenied("Only staff can verify companies")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company.verified = serializer.validated_data['verified']
        company.status = Company.Status.ACTIVE if company.verified else Company.Status.SUSPENDED
        company.save()
        
        return Response({'status': 'Company verification updated'})

class CompanyManagerViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyManagerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = self.request.query_params.get('company', None)
        if company:
            return User.objects.filter(managed_companies__id=company)
        return User.objects.none()

    def create(self, request):
        company = get_object_or_404(Company, pk=request.data.get('company'))
        if not company.managers.filter(pk=request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        
        user = get_object_or_404(User, pk=request.data.get('user'))
        company.managers.add(user)
        return Response({'status': 'Manager added'}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        company = get_object_or_404(Company, pk=request.data.get('company'))
        if not company.managers.filter(pk=request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        
        user = get_object_or_404(User, pk=pk)
        if company.managers.count() <= 1:
            return Response(
                {'error': 'Cannot remove the last manager'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        company.managers.remove(user)
        return Response({'status': 'Manager removed'})
