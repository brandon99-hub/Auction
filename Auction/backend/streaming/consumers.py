import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from auctions.models import Auction, Bid
from notifications.models import NotificationTemplate, NotificationLog, SMSNotification, EmailNotification
from payments.models import UserDeposit
import asyncio

User = get_user_model()

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'
        
        # Join auction group
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current auction state
        auction = await self.get_auction()
        if auction:
            await self.send(text_data=json.dumps({
                'type': 'auction_state',
                'current_price': str(auction.current_price),
                'status': auction.status,
                'end_time': auction.end_time.isoformat() if auction.end_time else None
            }))

    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'bid':
            user = self.scope['user']
            if not user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                return
                
            amount = float(data.get('amount'))
            success, message = await self.process_bid(user, amount)
            
            if success:
                # Broadcast new bid to all users in the auction
                await self.channel_layer.group_send(
                    self.auction_group_name,
                    {
                        'type': 'new_bid',
                        'user': user.username,
                        'amount': amount,
                        'message': message
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': message
                }))

    async def new_bid(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'user': event['user'],
            'amount': event['amount'],
            'message': event['message']
        }))

    @database_sync_to_async
    def get_auction(self):
        try:
            return Auction.objects.get(id=self.auction_id)
        except Auction.DoesNotExist:
            return None

    @database_sync_to_async
    def process_bid(self, user, amount):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            
            # Check if auction is active
            if auction.status != 'active':
                return False, 'Auction is not active'
                
            # Check if user has sufficient deposit
            required_deposit = auction.calculate_required_deposit()
            user_deposit = UserDeposit.objects.filter(
                user=user,
                status='completed'
            ).first()
            
            if not user_deposit or user_deposit.amount < required_deposit:
                return False, 'Insufficient deposit'
                
            # Check if bid is valid
            if amount <= auction.current_price:
                return False, 'Bid amount must be higher than current price'
                
            if amount < auction.current_price + auction.minimum_increment:
                return False, f'Bid must be at least {auction.minimum_increment} higher than current price'
                
            # Create new bid
            bid = Bid.objects.create(
                auction=auction,
                user=user,
                amount=amount
            )
            
            # Update auction current price
            auction.current_price = amount
            auction.save()
            
            # Notify outbid users
            self.notify_outbid_users(auction, bid)
            
            return True, 'Bid placed successfully'
            
        except Exception as e:
            return False, str(e)

    def notify_outbid_users(self, auction, new_bid):
        # Get previous highest bid
        previous_bid = Bid.objects.filter(
            auction=auction,
            is_winning=True
        ).first()
        
        if previous_bid and previous_bid.user != new_bid.user:
            # Create notification for outbid user
            template = NotificationTemplate.objects.get(event_type='outbid')
            notification = NotificationLog.objects.create(
                user=previous_bid.user,
                template=template,
                status='pending'
            )
            
            # Send SMS notification
            if previous_bid.user.notificationsettings.receive_sms:
                SMSNotification.objects.create(
                    notification_log=notification,
                    phone_number=previous_bid.user.phone_number,
                    message=template.message.format(
                        auction_title=auction.title,
                        amount=new_bid.amount
                    )
                )
            
            # Send email notification
            if previous_bid.user.notificationsettings.receive_email:
                EmailNotification.objects.create(
                    notification_log=notification,
                    email=previous_bid.user.email,
                    subject=template.subject,
                    message=template.message.format(
                        auction_title=auction.title,
                        amount=new_bid.amount
                    )
                )
            
            # Update bid status
            previous_bid.is_winning = False
            previous_bid.save()
            
        # Set new bid as winning
        new_bid.is_winning = True
        new_bid.save() 