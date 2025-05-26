from rest_framework import status, viewsets, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from .models import OAuthProfile, KYCVerification, SecurityLog, TwoFactorAuth, User
from .serializers import (
    OAuthLoginSerializer,
    KYCVerificationSerializer,
    SecurityLogSerializer,
    TwoFactorAuthSerializer
)
import onfido
from social_django.utils import load_strategy
import requests
from datetime import datetime, timedelta
import pyotp
import qrcode
import base64
from io import BytesIO
from rest_framework.views import APIView
import jwt

User = get_user_model()

class OAuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='google')
    def google_login(self, request):
        serializer = OAuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data['access_token']
        
        # Verify token with Google
        google_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if not google_response.ok:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            
        google_data = google_response.json()
        
        # Get or create user
        try:
            oauth_profile = OAuthProfile.objects.get(
                provider='google',
                provider_id=google_data['sub']
            )
            user = oauth_profile.user
        except OAuthProfile.DoesNotExist:
            user = User.objects.create_user(
                email=google_data['email'],
                username=google_data['email'],
                first_name=google_data.get('given_name', ''),
                last_name=google_data.get('family_name', ''),
                email_verified=True
            )
            
            OAuthProfile.objects.create(
                user=user,
                provider='google',
                provider_id=google_data['sub'],
                access_token=access_token
            )
        
        # Create security log
        SecurityLog.objects.create(
            user=user,
            event_type=SecurityLog.EventType.LOGIN,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            details={'provider': 'google'}
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

class KYCVerificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = KYCVerificationSerializer
    
    def get_queryset(self):
        return KYCVerification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        # Initialize Onfido client
        onfido_client = onfido.Api(settings.ONFIDO_API_TOKEN)
        
        # Create or get applicant
        try:
            kyc = KYCVerification.objects.get(user=request.user)
            applicant_id = kyc.onfido_applicant_id
        except KYCVerification.DoesNotExist:
            applicant = onfido_client.applicant.create({
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            })
            
            kyc = KYCVerification.objects.create(
                user=request.user,
                onfido_applicant_id=applicant.id
            )
            applicant_id = applicant.id
        
        # Create SDK token
        sdk_token = onfido_client.sdk_token.generate({
            'applicant_id': applicant_id,
            'referrer': settings.FRONTEND_URL
        })
        
        return Response({
            'sdk_token': sdk_token.token,
            'applicant_id': applicant_id
        })
    
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        event = request.data
        
        if event['payload']['resource_type'] == 'check' and event['payload']['action'] == 'check.completed':
            check_id = event['payload']['object']['id']
            applicant_id = event['payload']['object']['applicant_id']
            
            try:
                kyc = KYCVerification.objects.get(onfido_applicant_id=applicant_id)
                
                # Get check details from Onfido
                onfido_client = onfido.Api(settings.ONFIDO_API_TOKEN)
                check = onfido_client.check.find(check_id)
                
                if check.status == 'complete':
                    kyc.status = (
                        KYCVerification.Status.APPROVED 
                        if check.result == 'clear' 
                        else KYCVerification.Status.REJECTED
                    )
                    kyc.verified_at = timezone.now() if check.result == 'clear' else None
                    kyc.rejection_reason = check.result_uri if check.result != 'clear' else None
                    kyc.save()
                    
                    # Update user's KYC status
                    kyc.user.kyc_verified = check.result == 'clear'
                    kyc.user.save()
                    
                    # Create security log
                    SecurityLog.objects.create(
                        user=kyc.user,
                        event_type=SecurityLog.EventType.KYC_UPDATE,
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        details={
                            'status': kyc.status,
                            'check_id': check_id
                        }
                    )
            
            except KYCVerification.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_200_OK)

class SecurityLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SecurityLogSerializer
    
    def get_queryset(self):
        return SecurityLog.objects.filter(user=self.request.user).order_by('-created_at')

class TwoFactorAuthViewSet(viewsets.ModelViewSet):
    serializer_class = TwoFactorAuthSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TwoFactorAuth.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def setup(self, request):
        user = request.user
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            two_factor = TwoFactorAuth(user=user)
        
        # Generate a new secret key
        secret = pyotp.random_base32()
        two_factor.secret_key = secret
        two_factor.save()

        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(user.email, issuer_name="Auction Platform")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()

        return Response({
            'secret': secret,
            'qr_code': qr_code
        })

    @action(detail=False, methods=['post'])
    def verify(self, request):
        user = request.user
        code = request.data.get('code')
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            totp = pyotp.TOTP(two_factor.secret_key)
            
            if totp.verify(code):
                two_factor.is_enabled = True
                two_factor.save()
                return Response({'status': '2FA enabled successfully'})
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        except TwoFactorAuth.DoesNotExist:
            return Response({'error': '2FA not set up'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def disable(self, request):
        user = request.user
        code = request.data.get('code')
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            totp = pyotp.TOTP(two_factor.secret_key)
            
            if totp.verify(code):
                two_factor.is_enabled = False
                two_factor.save()
                return Response({'status': '2FA disabled successfully'})
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        except TwoFactorAuth.DoesNotExist:
            return Response({'error': '2FA not set up'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_backup_code(self, request):
        try:
            two_factor = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {'error': '2FA not set up'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Backup code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if two_factor.verify_backup_code(code):
            return Response({'status': 'Backup code verified successfully'})
        return Response(
            {'error': 'Invalid backup code'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def regenerate_backup_codes(self, request):
        try:
            two_factor = TwoFactorAuth.objects.get(user=request.user)
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {'error': '2FA not set up'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if two_factor.verify_token(token):
            backup_codes = two_factor.generate_backup_codes()
            two_factor.save()
            return Response({'backup_codes': backup_codes})
        return Response(
            {'error': 'Invalid token'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class WordPressAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate WordPress users with Django backend
        """
        username = request.data.get('username')
        password = request.data.get('password')

        # Verify credentials with WordPress
        wp_auth_url = f"{settings.WORDPRESS_URL}/wp-json/jwt-auth/v1/token"
        response = requests.post(wp_auth_url, data={
            'username': username,
            'password': password
        })

        if response.status_code != 200:
            return Response({'error': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)

        wp_user_data = response.json()
        
        # Create or update Django user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': wp_user_data.get('user_email'),
                'first_name': wp_user_data.get('user_nicename'),
                'is_active': True
            }
        )

        # Generate Django JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

class WordPressWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle WordPress webhooks for user actions
        """
        event = request.data.get('event')
        user_data = request.data.get('user')

        if event == 'user_created':
            User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'is_active': True
                }
            )
        elif event == 'user_updated':
            User.objects.filter(username=user_data['username']).update(
                email=user_data['email'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', '')
            )
        elif event == 'user_deleted':
            User.objects.filter(username=user_data['username']).delete()

        return Response({'status': 'success'})

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})

@api_view(['POST'])
@permission_classes([AllowAny])
def sync_user(request):
    try:
        # Verify JWT token
        token = request.headers.get('Authorization', '').split(' ')[1]
        payload = jwt.decode(token, settings.WORDPRESS_JWT_SECRET, algorithms=['HS256'])
        
        # Extract user data
        user_data = request.data
        username = user_data.get('username')
        email = user_data.get('email')
        
        # Update or create user
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'is_active': user_data.get('is_active', True)
            }
        )
        
        return Response({
            'status': 'success',
            'user_id': user.id,
            'created': created
        })
        
    except jwt.InvalidTokenError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 