# Auction Platform

A comprehensive auction platform with real-time bidding, video streaming, and secure payment processing.

## Features

- **Authentication & Security**
  - Email/password login
  - OAuth (Google, Facebook)
  - Two-Factor Authentication (2FA)
  - KYC verification via Onfido
  - Role-based access control

- **Multi-Company Support**
  - Company-specific dashboards
  - Custom branding
  - Seller and item management
  - Admin oversight

- **Auction Types**
  - Live Auctions
  - Timed Auctions
  - Buy Now Option
  - Reserve Price
  - Auto-bidding
  - Anti-sniping

- **Payment Processing**
  - Stripe
  - Braintree
  - M-Pesa
  - Cryptocurrency
  - Escrow system

- **Real-Time Features**
  - Live bidding
  - Chat system
  - Notifications (FCM, Email, SMS)
  - Video streaming

- **Analytics**
  - Google Analytics
  - Mixpanel/Amplitude
  - Company reports
  - Bid tracking
  - Sales analytics

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: ProBid WordPress site (https://probid-wp.egenstheme.com)
- **Database**: PostgreSQL
- **Real-Time**: Django Channels + Redis
- **Video**: Agora
- **Storage**: AWS S3
- **Monitoring**: Sentry
- **CI/CD**: GitHub Actions + Docker

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Docker (optional)
- WordPress (ProBid theme/site)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auction-platform.git
cd auction-platform
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

3. Configure environment variables:
```bash
# Backend (.env)
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/auction_platform
REDIS_URL=redis://localhost:6379/0
SENTRY_DSN=your_sentry_dsn
```

4. Run the backend development server:
```bash
python manage.py runserver
```

5. Set up the ProBid WordPress site:
- Deploy or configure your WordPress site using the ProBid theme at https://probid-wp.egenstheme.com or your chosen domain.
- Ensure the WordPress site is configured to communicate with the Django backend via REST API endpoints.
- (Optional) Install or develop custom plugins for auction integration, authentication, and real-time features as needed.

## Testing

```bash
# Backend tests
python manage.py test
```

## Deployment

The platform is configured for deployment on AWS using Docker:

```bash
# Build and run with Docker Compose
# (Frontend service is not included; use your WordPress deployment)
docker-compose up --build
```

## WordPress ↔ Django Integration

The ProBid WordPress site serves as the main frontend and communicates with the Django backend via REST APIs and real-time channels. Below are the main integration points:

- **API Base URL:** `https://your-backend-domain/api/`
- **Authentication:**
  - WordPress authenticates with Django using JWT tokens obtained from `/api/token/`.
  - API requests from WordPress should include the JWT token in the `Authorization` header.
- **Key Auction Endpoints:**
  - List auctions: `GET /api/auctions/`
  - Place bid: `POST /api/auctions/{id}/place_bid/`
  - Add to watchlist: `POST /api/auctions/{id}/add_to_watchlist/`
  - Notifications: `GET /api/notifications/`
- **Notifications/Webhooks:**
  - Django can notify WordPress of events (e.g., new bid, auction ended) via custom WordPress REST endpoints (e.g., `/wp-json/auctions/v1/notify-bid`).
- **Real-Time Features:**
  - WordPress can connect to Django Channels via WebSockets (e.g., `wss://your-backend-domain/ws/auctions/`) for live bidding and updates.
- **Custom Plugins:**
  - Custom WordPress plugins or code may be required to handle API calls, authentication, and real-time updates.

> **Note:** Adjust endpoint URLs and authentication details as needed for your deployment.

## Security

- HTTPS enforced
- CORS configured
- Rate limiting
- IP blocking
- CSRF protection
- XSS protection
- Secure headers

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@auctionplatform.com or create an issue in the repository. 