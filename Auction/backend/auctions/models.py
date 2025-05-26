from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import User
from companies.models import Company

class Auction(models.Model):
    """
    Represents an auction in the system.
    
    Business Logic:
    - Status Flow:
        draft -> pending -> active -> ended/cancelled
        - Draft: Initial state when auction is created
        - Pending: Waiting for admin approval
        - Active: Auction is live and accepting bids
        - Ended: Auction completed successfully
        - Cancelled: Auction terminated before completion
    
    - Price Management:
        - Start price: Initial price set by the company
        - Current price: Highest bid amount
        - Minimum increment: Minimum amount by which a bid must exceed current price
    
    - Time Management:
        - Start time: When auction becomes active
        - End time: When auction automatically ends
        - Duration must be between 1 hour and 30 days
    
    - Winner Determination:
        - Highest bidder at end time
        - Must meet reserve price if set
        - Must have valid payment method
    
    - Deposit Requirements:
        - Calculated as percentage of start price
        - Includes service fee
        - Required for bidding
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled')
    ]
    
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_increment = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_required_deposit(self):
        """
        Calculates the required deposit amount for bidding.
        
        Formula:
        deposit = (start_price * deposit_percentage / 100) + service_fee
        
        Returns:
            Decimal: The total deposit amount required
        """
        return (self.start_price * settings.PAYMENT_SETTINGS.deposit_percentage / 100) + settings.PAYMENT_SETTINGS.service_fee

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_winning = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-amount', 'created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.auction.title}"

class Item(models.Model):
    auction = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name='item')
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='auction_items/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.item.name}"

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='watchers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'auction')

    def __str__(self):
        return f"{self.user.username} watching {self.auction.title}"

class SavedAuction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'auction']

class AuctionNotification(models.Model):
    TYPE_CHOICES = [
        ('start', 'Auction Started'),
        ('outbid', 'You Were Outbid'),
        ('win', 'You Won'),
        ('end', 'Auction Ended'),
        ('cancelled', 'Auction Cancelled')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
