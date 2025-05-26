import requests
import base64
import datetime
from django.conf import settings
from .models import MpesaTransaction, PaymentSettings
import json
from cryptography.fernet import Fernet
from django.utils import timezone

class MpesaService:
    def __init__(self):
        self.settings = PaymentSettings.objects.first()
        self.access_token = None
        self.token_expiry = None

    def get_access_token(self):
        if self.access_token and self.token_expiry and timezone.now() < self.token_expiry:
            return self.access_token

        consumer_key = self.settings.mpesa_consumer_key
        consumer_secret = self.settings.mpesa_consumer_secret
        api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.token_expiry = timezone.now() + datetime.timedelta(seconds=data['expires_in'])
            return self.access_token
        else:
            raise Exception("Failed to get access token")

    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        access_token = self.get_access_token()
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{self.settings.mpesa_paybill}{self.settings.mpesa_passkey}{timestamp}".encode()
        ).decode()

        payload = {
            "BusinessShortCode": self.settings.mpesa_paybill,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.settings.mpesa_paybill,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.BASE_URL}/api/payments/mpesa/callback/",
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            data = response.json()
            return self.create_mpesa_transaction(data, phone_number, amount)
        else:
            raise Exception(f"STK Push failed: {response.text}")

    def create_mpesa_transaction(self, response_data, phone_number, amount):
        return MpesaTransaction.objects.create(
            phone_number=phone_number,
            amount=amount,
            transaction_id=response_data.get('MerchantRequestID'),
            checkout_request_id=response_data.get('CheckoutRequestID'),
            merchant_request_id=response_data.get('MerchantRequestID'),
            status='pending'
        )

    def process_callback(self, callback_data):
        try:
            transaction = MpesaTransaction.objects.get(
                checkout_request_id=callback_data['CheckoutRequestID']
            )
            
            if callback_data['ResultCode'] == 0:
                transaction.status = 'completed'
                # Process successful payment
                self.process_successful_payment(transaction)
            else:
                transaction.status = 'failed'
                # Handle failed payment
                self.process_failed_payment(transaction)
                
            transaction.save()
            return True
            
        except MpesaTransaction.DoesNotExist:
            return False

    def process_successful_payment(self, transaction):
        # Update user deposit
        user_deposit = UserDeposit.objects.create(
            user=transaction.user,
            amount=transaction.amount,
            status='completed',
            payment_method='mpesa',
            transaction_id=transaction.transaction_id
        )
        
        # Send confirmation notification
        self.send_payment_confirmation(transaction)

    def process_failed_payment(self, transaction):
        # Send failure notification
        self.send_payment_failure_notification(transaction)

    def send_payment_confirmation(self, transaction):
        # Implement notification sending logic
        pass

    def send_payment_failure_notification(self, transaction):
        # Implement notification sending logic
        pass

    def process_refund(self, transaction, amount):
        access_token = self.get_access_token()
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{self.settings.mpesa_paybill}{self.settings.mpesa_passkey}{timestamp}".encode()
        ).decode()

        payload = {
            "Initiator": self.settings.mpesa_paybill,
            "SecurityCredential": self.get_security_credential(),
            "CommandID": "TransactionReversal",
            "TransactionID": transaction.transaction_id,
            "Amount": amount,
            "ReceiverParty": transaction.phone_number,
            "RecieverIdentifierType": "4",
            "ResultURL": f"{settings.BASE_URL}/api/payments/mpesa/refund/callback/",
            "QueueTimeOutURL": f"{settings.BASE_URL}/api/payments/mpesa/refund/timeout/",
            "Remarks": "Refund for auction deposit",
            "Occasion": "Auction refund"
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/reversal/v1/request",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return True
        else:
            raise Exception(f"Refund failed: {response.text}")

    def get_security_credential(self):
        # Implement security credential generation
        pass 