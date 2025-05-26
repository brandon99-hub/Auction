from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OAuthProfile, KYCVerification, SecurityLog, TwoFactorAuth

User = get_user_model()

class OAuthLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    provider = serializers.ChoiceField(choices=['google', 'facebook'])

class OAuthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthProfile
        fields = ('provider', 'provider_id', 'expires_at')
        read_only_fields = fields

class KYCVerificationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = KYCVerification
        fields = (
            'id',
            'status',
            'status_display',
            'verified_at',
            'rejection_reason',
            'created_at',
            'updated_at'
        )
        read_only_fields = fields

class SecurityLogSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = SecurityLog
        fields = (
            'id',
            'event_type',
            'event_type_display',
            'ip_address',
            'user_agent',
            'created_at',
            'details'
        )
        read_only_fields = fields

class UserKYCSerializer(serializers.ModelSerializer):
    kyc_status = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'kyc_verified',
            'kyc_status'
        )
        read_only_fields = fields
    
    def get_kyc_status(self, obj):
        try:
            kyc = obj.kycverification
            return {
                'status': kyc.status,
                'status_display': kyc.get_status_display(),
                'verified_at': kyc.verified_at,
                'rejection_reason': kyc.rejection_reason
            }
        except KYCVerification.DoesNotExist:
            return None

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = TwoFactorAuth
        fields = ['id', 'user', 'is_enabled', 'created_at', 'updated_at', 'status']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_status(self, obj):
        return 'enabled' if obj.is_enabled else 'disabled'

    def validate_code(self, value):
        if not value or len(value) != 6 or not value.isdigit():
            raise serializers.ValidationError("Invalid verification code format")
        return value 