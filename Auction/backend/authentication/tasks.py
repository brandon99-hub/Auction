from celery import shared_task
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from .models import SecurityLog, TwoFactorAuth
from .utils import send_security_notification

@shared_task
def cleanup_expired_sessions():
    """Clean up expired sessions."""
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired_sessions.count()
    expired_sessions.delete()
    return f"Cleaned up {count} expired sessions"

@shared_task
def cleanup_old_security_logs():
    """Clean up security logs older than 30 days."""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    old_logs = SecurityLog.objects.filter(timestamp__lt=thirty_days_ago)
    count = old_logs.count()
    old_logs.delete()
    return f"Cleaned up {count} old security logs"

@shared_task
def send_security_alert(user_id, event_type, details):
    """Send security alert notification."""
    try:
        send_security_notification(user_id, event_type, details)
        return f"Security alert sent for user {user_id}"
    except Exception as e:
        return f"Failed to send security alert: {str(e)}"

@shared_task
def cleanup_expired_2fa_backup_codes():
    """Clean up expired 2FA backup codes."""
    expired_2fa = TwoFactorAuth.objects.filter(
        backup_codes_expiry__lt=timezone.now()
    )
    for two_factor in expired_2fa:
        two_factor.generate_backup_codes()
        two_factor.save()
    return f"Regenerated backup codes for {expired_2fa.count()} users" 