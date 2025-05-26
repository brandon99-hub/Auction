from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    GlobalAnalytics, UserAnalytics, AuctionAnalytics,
    FinancialReport, UserBiddingHistory, CompanyPerformanceReport
)
from auctions.models import Auction, Bid
from companies.models import Company
from users.models import User
from payments.models import UserDeposit

class AnalyticsService:
    def update_global_analytics(self):
        analytics, created = GlobalAnalytics.objects.get_or_create(pk=1)
        
        # Update user statistics
        analytics.total_users = User.objects.count()
        analytics.total_companies = Company.objects.count()
        
        # Update auction statistics
        analytics.total_auctions = Auction.objects.count()
        analytics.active_auctions = Auction.objects.filter(status='active').count()
        analytics.total_bids = Bid.objects.count()
        
        # Update financial statistics
        completed_auctions = Auction.objects.filter(status='ended')
        if completed_auctions.exists():
            analytics.total_revenue = completed_auctions.aggregate(
                total=Sum('current_price')
            )['total'] or 0
            analytics.average_sale_price = completed_auctions.aggregate(
                avg=Avg('current_price')
            )['avg'] or 0
        
        analytics.save()
        return analytics

    def update_user_analytics(self, user):
        analytics, created = UserAnalytics.objects.get_or_create(user=user)
        
        # Update bidding statistics
        user_bids = Bid.objects.filter(user=user)
        analytics.total_bids = user_bids.count()
        
        # Update winning statistics
        winning_bids = user_bids.filter(is_winning=True)
        analytics.total_wins = winning_bids.count()
        
        # Update financial statistics
        if user_bids.exists():
            analytics.total_spent = winning_bids.aggregate(
                total=Sum('amount')
            )['total'] or 0
            analytics.average_bid_amount = user_bids.aggregate(
                avg=Avg('amount')
            )['avg'] or 0
        
        analytics.save()
        return analytics

    def update_auction_analytics(self, auction):
        analytics, created = AuctionAnalytics.objects.get_or_create(auction=auction)
        
        # Update bid statistics
        bids = Bid.objects.filter(auction=auction)
        analytics.total_bids = bids.count()
        analytics.unique_bidders = bids.values('user').distinct().count()
        
        if bids.exists():
            analytics.highest_bid = bids.order_by('-amount').first().amount
            analytics.average_bid = bids.aggregate(avg=Avg('amount'))['avg']
        
        analytics.save()
        return analytics

    def generate_financial_report(self, period_type, start_date, end_date):
        report = FinancialReport.objects.create(
            period_type=period_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get completed auctions in the period
        completed_auctions = Auction.objects.filter(
            status='ended',
            end_time__range=[start_date, end_date]
        )
        
        report.number_of_auctions = completed_auctions.count()
        
        if completed_auctions.exists():
            # Calculate financial metrics
            financial_data = completed_auctions.aggregate(
                total_revenue=Sum('current_price'),
                average_sale_price=Avg('current_price')
            )
            
            report.total_revenue = financial_data['total_revenue'] or 0
            report.average_sale_price = financial_data['average_sale_price'] or 0
            
            # Calculate fees (5% of revenue)
            report.total_fees = report.total_revenue * 0.05
            report.net_earnings = report.total_revenue - report.total_fees
        
        report.save()
        return report

    def generate_user_bidding_history(self, user, start_date=None, end_date=None):
        query = Q(user=user)
        if start_date:
            query &= Q(created_at__gte=start_date)
        if end_date:
            query &= Q(created_at__lte=end_date)
            
        return UserBiddingHistory.objects.filter(query).order_by('-created_at')

    def generate_company_performance_report(self, company, start_date, end_date):
        report = CompanyPerformanceReport.objects.create(
            company=company,
            period_start=start_date,
            period_end=end_date
        )
        
        # Get company's auctions in the period
        company_auctions = Auction.objects.filter(
            company=company,
            end_time__range=[start_date, end_date]
        )
        
        report.total_auctions = company_auctions.count()
        report.successful_auctions = company_auctions.filter(status='ended').count()
        
        if company_auctions.exists():
            # Calculate financial metrics
            financial_data = company_auctions.aggregate(
                total_revenue=Sum('current_price'),
                average_sale_price=Avg('current_price')
            )
            
            report.total_revenue = financial_data['total_revenue'] or 0
            report.average_sale_price = financial_data['average_sale_price'] or 0
            
            # Calculate customer satisfaction (placeholder)
            report.customer_satisfaction = 4.5  # This should be calculated based on actual metrics
        
        report.save()
        return report

    def get_daily_metrics(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        return {
            'new_users': User.objects.filter(
                date_joined__date=today
            ).count(),
            'new_auctions': Auction.objects.filter(
                created_at__date=today
            ).count(),
            'active_auctions': Auction.objects.filter(
                status='active'
            ).count(),
            'total_bids': Bid.objects.filter(
                created_at__date=today
            ).count(),
            'revenue': Auction.objects.filter(
                status='ended',
                end_time__date=today
            ).aggregate(
                total=Sum('current_price')
            )['total'] or 0
        }

    def get_company_metrics(self, company):
        return {
            'total_auctions': Auction.objects.filter(company=company).count(),
            'active_auctions': Auction.objects.filter(
                company=company,
                status='active'
            ).count(),
            'completed_auctions': Auction.objects.filter(
                company=company,
                status='ended'
            ).count(),
            'total_revenue': Auction.objects.filter(
                company=company,
                status='ended'
            ).aggregate(
                total=Sum('current_price')
            )['total'] or 0,
            'average_sale_price': Auction.objects.filter(
                company=company,
                status='ended'
            ).aggregate(
                avg=Avg('current_price')
            )['avg'] or 0
        } 