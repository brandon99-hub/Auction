from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuctionViewSet,
    BidViewSet,
    ItemViewSet,
    WatchlistViewSet,
    SavedAuctionViewSet,
    AuctionNotificationViewSet,
    LiveAuctionView,
    AuctionSearchView,
)

router = DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')
router.register(r'bids', BidViewSet, basename='bid')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r'saved-auctions', SavedAuctionViewSet, basename='saved-auction')
router.register(r'notifications', AuctionNotificationViewSet, basename='notification')

urlpatterns = [
    path('live/<int:pk>/', LiveAuctionView.as_view({'get': 'retrieve'}), name='live-auction'),
    path('search/', AuctionSearchView.as_view({'get': 'list'}), name='auction-search'),
    path('', include(router.urls)),
]
