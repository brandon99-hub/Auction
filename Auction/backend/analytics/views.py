from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .tasks import generate_company_report, track_auction_event, track_user_activity
from companies.models import Company
from auctions.models import Auction
from users.models import User

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def company_report(self, request):
        """Get analytics report for a company."""
        company_id = request.query_params.get('company_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not all([company_id, start_date, end_date]):
            return Response({'error': 'Missing required parameters'}, status=400)

        # Check if user has permission to view company analytics
        company = Company.objects.get(id=company_id)
        if not (request.user.is_staff or request.user in company.managers.all()):
            return Response({'error': 'Not authorized to view company analytics'}, status=403)

        # Generate report
        report = generate_company_report.delay(company_id, start_date, end_date).get()
        
        if report:
            return Response(report)
        return Response({'error': 'Failed to generate report'}, status=500)

    @action(detail=False, methods=['get'])
    def auction_metrics(self, request):
        """Get metrics for a specific auction."""
        auction_id = request.query_params.get('auction_id')
        if not auction_id:
            return Response({'error': 'Missing auction_id parameter'}, status=400)

        try:
            auction = Auction.objects.get(id=auction_id)
            
            # Check if user has permission to view auction metrics
            if not (request.user.is_staff or 
                   request.user == auction.seller or 
                   request.user in auction.participants.all()):
                return Response({'error': 'Not authorized to view auction metrics'}, status=403)

            metrics = {
                'total_bids': auction.bids.count(),
                'unique_bidders': auction.bids.values('user').distinct().count(),
                'current_price': auction.current_price,
                'starting_price': auction.starting_price,
                'time_remaining': (auction.end_time - timezone.now()).total_seconds() if auction.end_time > timezone.now() else 0,
                'status': auction.status
            }

            return Response(metrics)

        except Auction.DoesNotExist:
            return Response({'error': 'Auction not found'}, status=404)

    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """Get user activity metrics."""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'Missing user_id parameter'}, status=400)

        try:
            user = User.objects.get(id=user_id)
            
            # Check if user has permission to view other user's activity
            if not (request.user.is_staff or request.user.id == int(user_id)):
                return Response({'error': 'Not authorized to view user activity'}, status=403)

            activity = {
                'total_bids': user.bids.count(),
                'auctions_participated': user.participated_auctions.count(),
                'auctions_won': user.won_auctions.count(),
                'total_spent': sum(auction.final_price for auction in user.won_auctions.all() if auction.final_price),
                'last_active': user.last_login.isoformat() if user.last_login else None
            }

            return Response(activity)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

    @action(detail=False, methods=['post'])
    def track_event(self, request):
        """Track a custom analytics event."""
        event_type = request.data.get('event_type')
        data = request.data.get('data', {})

        if not event_type:
            return Response({'error': 'Missing event_type parameter'}, status=400)

        # Track event
        track_user_activity.delay(request.user.id, event_type, data)
        
        return Response({'status': 'Event tracked successfully'}) 