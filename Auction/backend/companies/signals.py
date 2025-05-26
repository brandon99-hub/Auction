from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from .models import Company, CompanyDocument
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

@receiver(post_save, sender=Company)
def send_company_status_notification(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('status'):
        subject = f"Company Status Update: {instance.name}"
        message = f"Your company {instance.name} status has been updated to {instance.get_status_display()}"
        
        for manager in instance.managers.all():
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [manager.email],
                fail_silently=False,
            )

@receiver(post_save, sender=CompanyDocument)
def send_document_verification_notification(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('verified'):
        subject = f"Document Verification Update: {instance.get_document_type_display()}"
        status = "approved" if instance.verified else "rejected"
        message = f"Your {instance.get_document_type_display()} document for {instance.company.name} has been {status}."
        
        for manager in instance.company.managers.all():
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [manager.email],
                fail_silently=False,
            )

@receiver(m2m_changed, sender=Company.managers.through)
def check_minimum_managers(sender, instance, action, pk_set, **kwargs):
    if action == "pre_remove":
        if instance.managers.count() <= len(pk_set):
            raise Exception("A company must have at least one manager")

@receiver(pre_save, sender=Company)
def handle_company_verification(sender, instance, **kwargs):
    if instance.pk and instance.tracker.has_changed('verified'):
        if instance.verified:
            instance.status = Company.Status.ACTIVE
        else:
            instance.status = Company.Status.SUSPENDED
