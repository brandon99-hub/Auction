from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from users.serializers import UserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'auction', 'created_at', 'updated_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'user', 'content', 'created_at']
        read_only_fields = ['user', 'created_at'] 