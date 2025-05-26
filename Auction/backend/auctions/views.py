from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q
from .models import Auction, Bid, Item, Watchlist, SavedAuction, AuctionNotification
from .serializers import (
    AuctionSerializer,
    BidSerializer,
    ItemSerializer,
    WatchlistSerializer,
    LiveAuctionSerializer,
    SavedAuctionSerializer,
)
from .serializers import AuctionNotificationSerializer
from users.models import User
from companies.models import Company
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db import transaction
from datetime import timedelta
from .permissions import IsAuthenticatedOrReadOnly
import requests
from django.conf import settings

class AuctionNotificationViewSet(ModelViewSet):
    queryset = AuctionNotification.objects.all()
    serializer_class = AuctionNotificationSerializer

class SavedAuctionViewSet(ModelViewSet):
    queryset = SavedAuction.objects.all()
    serializer_class = SavedAuctionSerializer

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Filter auctions based on WordPress category
        """
        category = self.request.query_params.get('category', None)
        queryset = Auction.objects.all()
        
        if category:
            # Get WordPress category ID
            wp_category_url = f"{settings.WORDPRESS_URL}/wp-json/wp/v2/categories"
            response = requests.get(wp_category_url, params={'slug': category})
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    category_id = categories[0]['id']
                    queryset = queryset.filter(wordpress_category_id=category_id)
        
        return queryset

    def perform_create(self, serializer):
        company = get_object_or_404(Company, pk=self.request.data.get('company'))
        if not company.managers.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied("You are not a manager of this company")
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        auction = self.get_object()
        if auction.seller != request.user:
            return Response({'detail': 'Only the seller can start this auction'}, 
                          status=status.HTTP_403_FORBIDDEN)
        if auction.status != Auction.Status.DRAFT:
            return Response({'detail': 'Only draft auctions can be started'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        auction.status = Auction.Status.ACTIVE
        auction.save()
        return Response({'status': 'Auction started'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        auction = self.get_object()
        if auction.seller != request.user:
            return Response({'detail': 'Only the seller can cancel this auction'}, 
                          status=status.HTTP_403_FORBIDDEN)
        if auction.status not in [Auction.Status.DRAFT, Auction.Status.ACTIVE]:
            return Response({'detail': 'Only draft or active auctions can be cancelled'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        auction.status = Auction.Status.CANCELLED
        auction.save()
        return Response({'status': 'Auction cancelled'})

    @action(detail=True, methods=['post'])
    def place_bid(self, request, pk=None):
        """
        Handle bid placement from WordPress
        """
        auction = self.get_object()
        serializer = BidSerializer(data=request.data)
        
        if serializer.is_valid():
            bid = serializer.save(auction=auction, user=request.user)
            
            # Notify WordPress about new bid
            wp_notification_url = f"{settings.WORDPRESS_URL}/wp-json/auctions/v1/notify-bid"
            requests.post(wp_notification_url, json={
                'auction_id': auction.id,
                'bid_amount': bid.amount,
                'bidder_id': request.user.id
            })
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_to_watchlist(self, request, pk=None):
        """
        Add auction to user's watchlist
        """
        auction = self.get_object()
        Watchlist.objects.get_or_create(user=request.user, auction=auction)
        
        # Sync with WordPress
        wp_watchlist_url = f"{settings.WORDPRESS_URL}/wp-json/auctions/v1/watchlist"
        requests.post(wp_watchlist_url, json={
            'user_id': request.user.id,
            'auction_id': auction.id
        })
        
        return Response({'status': 'added to watchlist'})

class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        auction = self.request.query_params.get('auction', None)
        bidder = self.request.query_params.get('bidder', None)

        if auction:
            queryset = queryset.filter(auction_id=auction)
        if bidder:
            queryset = queryset.filter(bidder_id=bidder)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        auction_id = request.data.get('auction')
        amount = float(request.data.get('amount'))
        is_auto_bid = request.data.get('is_auto_bid', False)
        max_auto_bid = float(request.data.get('max_auto_bid', 0)) if is_auto_bid else None

        auction = get_object_or_404(Auction, pk=auction_id)
        
        if auction.status != Auction.Status.ACTIVE:
            return Response({'detail': 'Bids can only be placed on active auctions'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if auction.seller == request.user:
            return Response({'detail': 'You cannot bid on your own auction'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if amount <= (auction.current_price or auction.starting_price):
            return Response({'detail': 'Bid amount must be higher than current price'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if is_auto_bid and max_auto_bid <= amount:
            return Response({'detail': 'Max auto bid must be higher than initial bid'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Handle anti-sniping
        if auction.end_time - timezone.now() <= timedelta(minutes=auction.anti_sniping_minutes):
            auction.end_time += timedelta(minutes=auction.anti_sniping_minutes)
            auction.save()

        bid = Bid.objects.create(
            auction=auction,
            bidder=request.user,
            amount=amount,
            is_auto_bid=is_auto_bid,
            max_auto_bid=max_auto_bid
        )

        auction.current_price = amount
        auction.save()

        serializer = self.get_serializer(bid)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Create item with WordPress media integration
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Upload images to WordPress media library
        images = request.FILES.getlist('images')
        wp_media_url = f"{settings.WORDPRESS_URL}/wp-json/wp/v2/media"
        
        media_ids = []
        for image in images:
            response = requests.post(
                wp_media_url,
                files={'file': image},
                headers={'Authorization': f'Bearer {request.auth}'}
            )
            if response.status_code == 201:
                media_ids.append(response.json()['id'])
        
        # Create item with WordPress media IDs
        item = serializer.save(wordpress_media_ids=media_ids)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LiveAuctionView(viewsets.GenericViewSet):
    serializer_class = LiveAuctionSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        auction = get_object_or_404(Auction, pk=pk)
        if auction.status != Auction.Status.ACTIVE:
            return Response({'detail': 'This auction is not currently active'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(auction)
        return Response(serializer.data)

class AuctionSearchView(viewsets.GenericViewSet):
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Auction.objects.filter(status=Auction.Status.ACTIVE)
        search = request.query_params.get('q', None)
        category = request.query_params.get('category', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(item__name__icontains=search) |
                Q(item__description__icontains=search)
            ).distinct()
        if category:
            queryset = queryset.filter(item__category=category)
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
