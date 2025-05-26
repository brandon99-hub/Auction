from django.db import models
from django.utils import timezone
from django.conf import settings

class GlobalAnalytics(models.Model):
    total_users = models.PositiveIntegerField(default=0)
    total_companies = models.PositiveIntegerField(default=0)
    total_auctions = models.PositiveIntegerField(default=0)
    active_auctions = models.PositiveIntegerField(default=0)
    total_bids = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

class UserAnalytics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_bids = models.PositiveIntegerField(default=0)
    total_wins = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_bid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

class AuctionAnalytics(models.Model):
    auction = models.ForeignKey('auctions.Auction', on_delete=models.CASCADE)
    total_bids = models.PositiveIntegerField(default=0)
    unique_bidders = models.PositiveIntegerField(default=0)
    highest_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    views = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

class FinancialReport(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ]
    
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_fees = models.DecimalField(max_digits=12, decimal_places=2)
    net_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_auctions = models.PositiveIntegerField()
    average_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

class UserBiddingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    auction = models.ForeignKey('auctions.Auction', on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_winning = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

class CompanyPerformanceReport(models.Model):
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    total_auctions = models.PositiveIntegerField()
    successful_auctions = models.PositiveIntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    average_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_satisfaction = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now) 