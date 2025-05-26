from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from companies.models import Company
from auctions.models import Auction

User = get_user_model()

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.admin = User.objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        
        self.company_manager = User.objects.create_user(
            email='manager@test.com',
            password='testpass123',
            role='company_manager'
        )
        
        self.seller = User.objects.create_user(
            email='seller@test.com',
            password='testpass123',
            role='seller'
        )
        
        self.bidder = User.objects.create_user(
            email='bidder@test.com',
            password='testpass123',
            role='bidder'
        )
        
        # Create test company
        self.company = Company.objects.create(
            name='Test Company',
            manager=self.company_manager
        )
        
        # Create test auction
        self.auction = Auction.objects.create(
            title='Test Auction',
            description='Test Description',
            company=self.company,
            seller=self.seller,
            starting_price=100.00,
            reserve_price=200.00
        )
    
    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authenticate_user(self, user):
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def create_test_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        image = Image.new('RGB', (100, 100))
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        return SimpleUploadedFile(
            'test_image.jpg',
            image_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def create_test_video(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        return SimpleUploadedFile(
            'test_video.mp4',
            b'fake video content',
            content_type='video/mp4'
        ) 