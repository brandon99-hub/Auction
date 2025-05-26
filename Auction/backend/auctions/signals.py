from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Auction, Bid
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

@receiver(pre_save, sender=Auction)
def check_auction_status(sender, instance, **kwargs):
    if instance.pk:
        original = Auction.objects.get(pk=instance.pk)
        if original.status != instance.status and instance.status == Auction.Status.ACTIVE:
            instance.start_time = timezone.now()
        elif original.status != instance.status and instance.status == Auction.Status.COMPLETED:
            instance.end_time = timezone.now()

@receiver(post_save, sender=Bid)
def handle_new_bid(sender, instance, created, **kwargs):
    if created:
        auction = instance.auction
        # Notify seller
        send_mail(
            'New Bid on Your Auction',
            f'Your auction "{auction.title}" received a new bid of {instance.amount}',
            settings.DEFAULT_FROM_EMAIL,
            [auction.seller.email],
            fail_silently=False,
        )
        
        # Check for auto-bidding
        if instance.is_auto_bid:
            highest_bid = auction.bids.exclude(pk=instance.pk).order_by('-amount').first()
            if highest_bid and highest_bid.is_auto_bid and highest_bid.max_auto_bid > instance.amount:
                increment = auction.bid_increment
                new_amount = min(instance.amount + increment, highest_bid.max_auto_bid)
                if new_amount > instance.amount:
                    Bid.objects.create(
                        auction=auction,
                        bidder=highest_bid.bidder,
                        amount=new_amount,
                        is_auto_bid=True,
                        max_auto_bid=highest_bid.max_auto_bid
                    )

@receiver(post_save, sender=Auction)
def check_auction_completion(sender, instance, created, **kwargs):
    if not created and instance.status == Auction.Status.ACTIVE and instance.end_time <= timezone.now():
        instance.status = Auction.Status.COMPLETED
        instance.save()
        
        # Notify winner and seller
        winning_bid = instance.bids.order_by('-amount').first()
        if winning_bid:
            send_mail(
                'Auction Won',
                f'You won the auction for "{instance.title}" with a bid of {winning_bid.amount}',
                settings.DEFAULT_FROM_EMAIL,
                [winning_bid.bidder.email],
                fail_silently=False,
            )
            
            send_mail(
                'Auction Completed',
                f'Your auction "{instance.title}" sold for {winning_bid.amount}',
                settings.DEFAULT_FROM_EMAIL,
                [instance.seller.email],
                fail_silently=False,
            )
