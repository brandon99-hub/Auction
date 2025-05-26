import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Auction, Bid
from django.contrib.auth import get_user_model

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

    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'bid':
            # Handle bid placement
            user = self.scope['user']
            amount = text_data_json['amount']
            
            # Create bid
            bid = await self.create_bid(user, amount)
            
            if bid:
                # Send bid notification to group
                await self.channel_layer.group_send(
                    self.auction_group_name,
                    {
                        'type': 'bid_message',
                        'bid': {
                            'user': {
                                'username': user.username,
                                'id': user.id
                            },
                            'amount': str(amount),
                            'created_at': bid.created_at.isoformat()
                        }
                    }
                )

    async def bid_message(self, event):
        # Send bid message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'bid',
            'bid': event['bid']
        }))

    @database_sync_to_async
    def create_bid(self, user, amount):
        try:
            auction = Auction.objects.get(id=self.auction_id)
            if auction.status != 'active':
                return None
            
            bid = Bid.objects.create(
                auction=auction,
                user=user,
                amount=amount
            )
            
            # Update auction current price
            auction.current_price = amount
            auction.save()
            
            return bid
        except Auction.DoesNotExist:
            return None 