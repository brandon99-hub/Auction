from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Auction, Bid
from .utils import notify_auction_winner, notify_auction_ended

@shared_task
def check_auction_status():
    """Check and update auction statuses."""
    now = timezone.now()
    
    # End auctions that have passed their end time
    ended_auctions = Auction.objects.filter(
        status='active',
        end_time__lt=now
    )
    
    for auction in ended_auctions:
        auction.status = 'ended'
        auction.save()
        
        # Notify winner if there are bids
        winning_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        if winning_bid:
            notify_auction_winner(auction, winning_bid)
        else:
            notify_auction_ended(auction)

    # Start auctions that have reached their start time
    starting_auctions = Auction.objects.filter(
        status='scheduled',
        start_time__lte=now
    )
    
    for auction in starting_auctions:
        auction.status = 'active'
        auction.save()

    return f"Updated {ended_auctions.count()} ended auctions and {starting_auctions.count()} starting auctions"

@shared_task
def cleanup_old_auctions():
    """Clean up old auction data."""
    three_months_ago = timezone.now() - timedelta(days=90)
    
    # Archive old ended auctions
    old_auctions = Auction.objects.filter(
        status='ended',
        end_time__lt=three_months_ago
    )
    
    for auction in old_auctions:
        auction.status = 'archived'
        auction.save()
    
    return f"Archived {old_auctions.count()} old auctions"

@shared_task
def send_auction_reminders():
    """Send reminders for upcoming auctions."""
    one_hour_from_now = timezone.now() + timedelta(hours=1)
    upcoming_auctions = Auction.objects.filter(
        status='scheduled',
        start_time__lte=one_hour_from_now,
        start_time__gt=timezone.now()
    )
    
    for auction in upcoming_auctions:
        # Notify users who have shown interest
        interested_users = auction.watchlist.all()
        for user in interested_users:
            user.notify(
                'auction_reminder',
                {
                    'auction_id': auction.id,
                    'auction_title': auction.title,
                    'start_time': auction.start_time
                }
            )
    
    return f"Sent reminders for {upcoming_auctions.count()} upcoming auctions" 