import requests
from django.conf import settings
from .models import NotificationTemplate, NotificationLog, SMSNotification, EmailNotification
from django.utils import timezone
import json

class NotificationService:
    def __init__(self):
        self.africas_talking_api_key = settings.AFRICAS_TALKING_API_KEY
        self.africas_talking_username = settings.AFRICAS_TALKING_USERNAME
        self.sendgrid_api_key = settings.SENDGRID_API_KEY

    def send_sms(self, phone_number, message):
        url = "https://api.africastalking.com/version1/messaging"
        headers = {
            "apiKey": self.africas_talking_api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "username": self.africas_talking_username,
            "to": phone_number,
            "message": message
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response_data = response.json()
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message_id': response_data.get('SMSMessageData', {}).get('MessageId'),
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('SMSMessageData', {}).get('Message'),
                    'status': 'failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }

    def send_email(self, to_email, subject, message):
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}]
                }
            ],
            "from": {"email": settings.DEFAULT_FROM_EMAIL},
            "subject": subject,
            "content": [
                {
                    "type": "text/plain",
                    "value": message
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 202:
                return {
                    'success': True,
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'error': response.text,
                    'status': 'failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }

    def process_notification(self, notification_log):
        template = notification_log.template
        user = notification_log.user
        
        if template.notification_type in ['sms', 'both'] and user.notificationsettings.receive_sms:
            sms_notification = SMSNotification.objects.create(
                notification_log=notification_log,
                phone_number=user.phone_number,
                message=template.message
            )
            
            result = self.send_sms(user.phone_number, template.message)
            sms_notification.status = result['status']
            sms_notification.provider_response = result
            sms_notification.save()
            
        if template.notification_type in ['email', 'both'] and user.notificationsettings.receive_email:
            email_notification = EmailNotification.objects.create(
                notification_log=notification_log,
                email=user.email,
                subject=template.subject,
                message=template.message
            )
            
            result = self.send_email(user.email, template.subject, template.message)
            email_notification.status = result['status']
            email_notification.provider_response = result
            email_notification.save()
            
        # Update notification log status
        notification_log.status = 'sent'
        notification_log.save()

    def send_auction_notification(self, event_type, auction, user, **kwargs):
        try:
            template = NotificationTemplate.objects.get(event_type=event_type)
            notification = NotificationLog.objects.create(
                user=user,
                template=template,
                status='pending'
            )
            
            # Format message with auction details
            formatted_message = template.message.format(
                auction_title=auction.title,
                current_price=auction.current_price,
                **kwargs
            )
            
            # Update notification with formatted message
            notification.message = formatted_message
            notification.save()
            
            # Process notification
            self.process_notification(notification)
            
            return True
            
        except NotificationTemplate.DoesNotExist:
            return False

    def send_payment_notification(self, event_type, transaction, **kwargs):
        try:
            template = NotificationTemplate.objects.get(event_type=event_type)
            notification = NotificationLog.objects.create(
                user=transaction.user,
                template=template,
                status='pending'
            )
            
            # Format message with transaction details
            formatted_message = template.message.format(
                amount=transaction.amount,
                transaction_id=transaction.transaction_id,
                **kwargs
            )
            
            # Update notification with formatted message
            notification.message = formatted_message
            notification.save()
            
            # Process notification
            self.process_notification(notification)
            
            return True
            
        except NotificationTemplate.DoesNotExist:
            return False 