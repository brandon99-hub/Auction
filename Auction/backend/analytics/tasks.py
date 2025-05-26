from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests
import json
from auctions.models import Auction, Bid
from users.models import User
from companies.models import Company
from .models import AnalyticsEvent, CompanyAnalytics, UserAnalytics
from .utils import generate_analytics_report, send_analytics_email

@shared_task
def track_auction_event(event_type, auction_id, user_id=None, data=None):
    """Track auction-related events in analytics services."""
    try:
        auction = Auction.objects.get(id=auction_id)
        user = User.objects.get(id=user_id) if user_id else None
        
        event_data = {
            'event_type': event_type,
            'auction_id': auction_id,
            'auction_title': auction.title,
            'auction_type': auction.auction_type,
            'company_id': auction.company.id,
            'timestamp': timezone.now().isoformat(),
            'data': data or {}
        }
        
        if user:
            event_data['user_id'] = user_id
            event_data['user_email'] = user.email
            event_data['user_role'] = user.role

        # Track in Mixpanel
        if settings.MIXPANEL_API_TOKEN:
            requests.post(
                'https://api.mixpanel.com/track',
                data={
                    'data': json.dumps({
                        'event': event_type,
                        'properties': {
                            'distinct_id': user_id or 'anonymous',
                            'token': settings.MIXPANEL_API_TOKEN,
                            **event_data
                        }
                    })
                }
            )

        # Track in Amplitude
        if settings.AMPLITUDE_API_KEY:
            requests.post(
                'https://api2.amplitude.com/2/httpapi',
                json={
                    'api_key': settings.AMPLITUDE_API_KEY,
                    'events': [{
                        'user_id': user_id or 'anonymous',
                        'event_type': event_type,
                        'time': int(timezone.now().timestamp() * 1000),
                        'event_properties': event_data
                    }]
                }
            )

    except Exception as e:
        print(f"Error tracking analytics event: {str(e)}")

@shared_task
def generate_company_report(company_id, start_date, end_date):
    """Generate analytics report for a company."""
    try:
        company = Company.objects.get(id=company_id)
        start = timezone.datetime.fromisoformat(start_date)
        end = timezone.datetime.fromisoformat(end_date)

        # Get auctions in date range
        auctions = Auction.objects.filter(
            company=company,
            created_at__range=(start, end)
        )

        # Calculate metrics
        total_auctions = auctions.count()
        active_auctions = auctions.filter(status='active').count()
        completed_auctions = auctions.filter(status='completed').count()
        total_bids = Bid.objects.filter(auction__in=auctions).count()
        total_revenue = sum(auction.final_price or 0 for auction in auctions if auction.status == 'completed')

        # Get user metrics
        unique_bidders = User.objects.filter(
            bids__auction__in=auctions
        ).distinct().count()

        # Generate report
        report = {
            'company_id': company_id,
            'company_name': company.name,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'metrics': {
                'total_auctions': total_auctions,
                'active_auctions': active_auctions,
                'completed_auctions': completed_auctions,
                'total_bids': total_bids,
                'total_revenue': total_revenue,
                'unique_bidders': unique_bidders,
                'average_bids_per_auction': total_bids / total_auctions if total_auctions > 0 else 0,
                'average_revenue_per_auction': total_revenue / completed_auctions if completed_auctions > 0 else 0
            }
        }

        # Store report in database or send via email
        # Implementation depends on requirements

        return report

    except Exception as e:
        print(f"Error generating company report: {str(e)}")
        return None

@shared_task
def track_user_activity(user_id, event_type, data=None):
    """Track user activity in analytics services."""
    try:
        user = User.objects.get(id=user_id)
        
        event_data = {
            'event_type': event_type,
            'user_id': user_id,
            'user_email': user.email,
            'user_role': user.role,
            'timestamp': timezone.now().isoformat(),
            'data': data or {}
        }

        # Track in Mixpanel
        if settings.MIXPANEL_API_TOKEN:
            requests.post(
                'https://api.mixpanel.com/track',
                data={
                    'data': json.dumps({
                        'event': event_type,
                        'properties': {
                            'distinct_id': user_id,
                            'token': settings.MIXPANEL_API_TOKEN,
                            **event_data
                        }
                    })
                }
            )

        # Track in Amplitude
        if settings.AMPLITUDE_API_KEY:
            requests.post(
                'https://api2.amplitude.com/2/httpapi',
                json={
                    'api_key': settings.AMPLITUDE_API_KEY,
                    'events': [{
                        'user_id': user_id,
                        'event_type': event_type,
                        'time': int(timezone.now().timestamp() * 1000),
                        'event_properties': event_data
                    }]
                }
            )

    except Exception as e:
        print(f"Error tracking user activity: {str(e)}")

@shared_task
def aggregate_daily_analytics():
    """Aggregate daily analytics data."""
    yesterday = timezone.now() - timedelta(days=1)
    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Aggregate user analytics
    user_events = AnalyticsEvent.objects.filter(
        timestamp__range=(start_date, end_date),
        event_type__in=['login', 'auction_view', 'bid_placed']
    )
    
    for user_id in user_events.values_list('user_id', flat=True).distinct():
        user_analytics, _ = UserAnalytics.objects.get_or_create(
            user_id=user_id,
            date=yesterday.date()
        )
        user_analytics.update_metrics(user_events.filter(user_id=user_id))
        user_analytics.save()

    # Aggregate company analytics
    company_events = AnalyticsEvent.objects.filter(
        timestamp__range=(start_date, end_date),
        event_type__in=['auction_created', 'auction_ended', 'bid_received']
    )
    
    for company_id in company_events.values_list('company_id', flat=True).distinct():
        company_analytics, _ = CompanyAnalytics.objects.get_or_create(
            company_id=company_id,
            date=yesterday.date()
        )
        company_analytics.update_metrics(company_events.filter(company_id=company_id))
        company_analytics.save()

    return "Daily analytics aggregated successfully"

@shared_task
def send_daily_analytics():
    """Send daily analytics reports to companies."""
    yesterday = timezone.now() - timedelta(days=1)
    companies = CompanyAnalytics.objects.filter(date=yesterday.date())
    
    for company_analytics in companies:
        report = generate_analytics_report(company_analytics)
        send_analytics_email(company_analytics.company, report)
    
    return f"Sent analytics reports to {companies.count()} companies"

@shared_task
def cleanup_old_analytics():
    """Clean up analytics data older than 1 year."""
    one_year_ago = timezone.now() - timedelta(days=365)
    
    # Delete old events
    old_events = AnalyticsEvent.objects.filter(timestamp__lt=one_year_ago)
    events_count = old_events.count()
    old_events.delete()
    
    # Delete old aggregated data
    old_user_analytics = UserAnalytics.objects.filter(date__lt=one_year_ago.date())
    old_company_analytics = CompanyAnalytics.objects.filter(date__lt=one_year_ago.date())
    
    user_count = old_user_analytics.count()
    company_count = old_company_analytics.count()
    
    old_user_analytics.delete()
    old_company_analytics.delete()
    
    return f"Cleaned up {events_count} events, {user_count} user analytics, and {company_count} company analytics" 