from rest_framework import serializers
from .models import Company, CompanyAddress, CompanyDocument
from users.serializers import UserProfileSerializer
from users.models import User

class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAddress
        fields = '__all__'
        read_only_fields = ('company',)

class CompanyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocument
        fields = '__all__'
        read_only_fields = ('company', 'uploaded_at')

class CompanySerializer(serializers.ModelSerializer):
    addresses = CompanyAddressSerializer(many=True, read_only=True)
    documents = CompanyDocumentSerializer(many=True, read_only=True)
    managers = UserProfileSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'verified', 'status')

    def validate(self, data):
        if self.instance and 'managers' in data:
            if not data['managers']:
                raise serializers.ValidationError("A company must have at least one manager")
        return data

class CompanyVerificationSerializer(serializers.Serializer):
    verified = serializers.BooleanField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)

class CompanyManagerSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'company', 'user')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},
            'email': {'read_only': True},
        }

    def validate(self, data):
        company = data['company']
        user = data['user']
        if company.managers.filter(pk=user.pk).exists():
            raise serializers.ValidationError("This user is already a manager of the company")
        return data
