from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import pyotp
import qrcode
import io
import base64
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.files.base import ContentFile

User = get_user_model()

class OAuthProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    provider = models.CharField(max_length=30)
    provider_id = models.CharField(max_length=100)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('provider', 'provider_id')

class KYCVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    onfido_applicant_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

class SecurityLog(models.Model):
    class EventType(models.TextChoices):
        LOGIN = 'LOGIN', _('Login')
        LOGOUT = 'LOGOUT', _('Logout')
        PASSWORD_CHANGE = 'PASSWORD_CHANGE', _('Password Change')
        PASSWORD_RESET = 'PASSWORD_RESET', _('Password Reset')
        TWO_FACTOR_ENABLE = 'TWO_FACTOR_ENABLE', _('2FA Enable')
        TWO_FACTOR_DISABLE = 'TWO_FACTOR_DISABLE', _('2FA Disable')
        KYC_UPDATE = 'KYC_UPDATE', _('KYC Update')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.event_type} - {self.created_at}"

class LoginAttempt(models.Model):
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'ip_address', 'created_at']),
        ]

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=32)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Two Factor Authentication"
        verbose_name_plural = "Two Factor Authentications"

    def __str__(self):
        return f"2FA for {self.user.email}"

    def generate_secret_key(self):
        self.secret_key = pyotp.random_base32()
        return self.secret_key

    def generate_backup_codes(self, count=10):
        codes = [pyotp.random_base32()[:8] for _ in range(count)]
        self.backup_codes = codes
        return codes

    def verify_token(self, token):
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token)

    def get_provisioning_uri(self):
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name='Auction Platform'
        )

    def generate_qr_code(self):
        uri = self.get_provisioning_uri()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

    def verify_backup_code(self, code):
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False


class UserVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_type = models.CharField(max_length=20)  # phone, email, id
    verification_status = models.CharField(max_length=20)  # pending, approved, rejected
    verification_document = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True) 