import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'chat_message':
            message = text_data_json.get('message')
            user = self.scope['user']

            if not user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You must be logged in to send messages'
                }))
                return

            # Process the message
            chat_message = await self.process_message(user, message)
            if chat_message:
                # Broadcast the message to the room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': ChatMessageSerializer(chat_message).data
                    }
                )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def process_message(self, user, content):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            
            # Create new message
            message = ChatMessage.objects.create(
                room=room,
                user=user,
                content=content
            )

            return message
        except ChatRoom.DoesNotExist:
            return None 