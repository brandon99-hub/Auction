from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Auction, Bid, Item, ItemImage, Watchlist, SavedAuction, AuctionNotification
from users.serializers import UserProfileSerializer
from companies.serializers import CompanySerializer

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'is_primary', 'caption']
        read_only_fields = ['id']

    def validate_image(self, value):
        """Validate image size and format"""
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Image size cannot exceed 5MB")
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("File must be an image")
        return value

class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, required=False)
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'category', 'condition', 
                 'dimensions', 'weight', 'manufacturer', 'model_number', 
                 'serial_number', 'images']
        read_only_fields = ['id']

    def validate(self, data):
        """Validate item data"""
        if data.get('weight') and data['weight'] <= 0:
            raise serializers.ValidationError("Weight must be positive")
        return data

class AuctionSerializer(serializers.ModelSerializer):
    seller = UserProfileSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    item = ItemSerializer()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = ['id', 'company', 'title', 'description', 'start_price', 
                 'current_price', 'minimum_increment', 'start_time', 'end_time', 
                 'status', 'winner', 'item']
        read_only_fields = ['id', 'current_price', 'winner']

    def validate(self, data):
        """Validate auction data"""
        # Validate time constraints
        if data['start_time'] < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past")
        
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time")
        
        # Validate duration (1 hour to 30 days)
        duration = data['end_time'] - data['start_time']
        if duration < timedelta(hours=1):
            raise serializers.ValidationError("Auction duration must be at least 1 hour")
        if duration > timedelta(days=30):
            raise serializers.ValidationError("Auction duration cannot exceed 30 days")
        
        # Validate price constraints
        if data['start_price'] <= 0:
            raise serializers.ValidationError("Start price must be positive")
        
        if data['minimum_increment'] <= 0:
            raise serializers.ValidationError("Minimum increment must be positive")
        
        if data['minimum_increment'] >= data['start_price']:
            raise serializers.ValidationError("Minimum increment must be less than start price")
        
        return data

    def get_time_remaining(self, obj):
        if obj.status == obj.Status.ACTIVE:
            return (obj.end_time - self.context['request'].now()).total_seconds()
        return None

    def get_is_active(self, obj):
        return obj.status == obj.Status.ACTIVE

class BidSerializer(serializers.ModelSerializer):
    bidder = UserProfileSerializer(read_only=True)
    auction = serializers.PrimaryKeyRelatedField(queryset=Auction.objects.all())

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'user', 'amount', 'is_winning', 'created_at']
        read_only_fields = ['id', 'user', 'is_winning', 'created_at']

    def validate(self, data):
        """Validate bid data"""
        auction = data['auction']
        
        # Check if auction is active
        if auction.status != 'active':
            raise serializers.ValidationError("Cannot bid on inactive auction")
        
        # Check if auction has ended
        if auction.end_time < timezone.now():
            raise serializers.ValidationError("Auction has ended")
        
        # Validate bid amount
        if data['amount'] <= auction.current_price:
            raise serializers.ValidationError("Bid amount must be higher than current price")
        
        if data['amount'] - auction.current_price < auction.minimum_increment:
            raise serializers.ValidationError(f"Bid must increase by at least {auction.minimum_increment}")
        
        return data

class WatchlistSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    auction = serializers.PrimaryKeyRelatedField(queryset=Auction.objects.all())

    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'auction', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):
        """Validate watchlist data"""
        # Check if auction is already in user's watchlist
        if Watchlist.objects.filter(user=data['user'], auction=data['auction']).exists():
            raise serializers.ValidationError("Auction is already in your watchlist")
        return data

class SavedAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedAuction
        fields = ['id', 'user', 'auction', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):
        """Validate saved auction data"""
        # Check if auction is already saved by user
        if SavedAuction.objects.filter(user=data['user'], auction=data['auction']).exists():
            raise serializers.ValidationError("Auction is already saved")
        return data

class AuctionNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionNotification
        fields = ['id', 'user', 'auction', 'notification_type', 'message', 
                 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_notification_type(self, value):
        """Validate notification type"""
        valid_types = [choice[0] for choice in AuctionNotification.TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError("Invalid notification type")
        return value

class LiveAuctionSerializer(serializers.ModelSerializer):
    seller = UserProfileSerializer(read_only=True)
    item = ItemSerializer(read_only=True)
    current_bid = serializers.SerializerMethodField()
    bid_history = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time', 
            'starting_price', 'current_price', 'reserve_price', 
            'bid_increment', 'seller', 'item', 'current_bid', 
            'bid_history', 'time_remaining'
        ]

    def get_current_bid(self, obj):
        highest_bid = obj.bids.order_by('-amount').first()
        if highest_bid:
            return BidSerializer(highest_bid).data
        return None

    def get_bid_history(self, obj):
        bids = obj.bids.order_by('-amount')[:10]
        return BidSerializer(bids, many=True).data

    def get_time_remaining(self, obj):
        return (obj.end_time - self.context['request'].now()).total_seconds()
