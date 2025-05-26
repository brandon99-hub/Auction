from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        COMPANY_MANAGER = 'COMPANY_MANAGER', _('Company Manager')
        SELLER = 'SELLER', _('Seller')
        BIDDER = 'BIDDER', _('Bidder')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BIDDER)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    kyc_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    mpesa_paybill = models.CharField(max_length=10, blank=True, null=True)
    mpesa_account = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
