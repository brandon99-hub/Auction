from django.db import models
from django.utils import timezone
from django.conf import settings

class NotificationTemplate(models.Model):
    TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('both', 'Both')
    ]
    
    EVENT_CHOICES = [
        ('auction_start', 'Auction Started'),
        ('outbid', 'Outbid'),
        ('win', 'Auction Won'),
        ('loss', 'Auction Lost'),
        ('refund', 'Refund Processed'),
        ('deposit', 'Deposit Required'),
        ('company_approved', 'Company Approved'),
        ('company_rejected', 'Company Rejected')
    ]
    
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class SMSNotification(models.Model):
    notification_log = models.ForeignKey(NotificationLog, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=NotificationLog.STATUS_CHOICES, default='pending')
    provider_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class EmailNotification(models.Model):
    notification_log = models.ForeignKey(NotificationLog, on_delete=models.CASCADE)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=NotificationLog.STATUS_CHOICES, default='pending')
    provider_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class NotificationSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)
    auction_start = models.BooleanField(default=True)
    outbid = models.BooleanField(default=True)
    win = models.BooleanField(default=True)
    loss = models.BooleanField(default=True)
    refund = models.BooleanField(default=True)
    deposit = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True) 