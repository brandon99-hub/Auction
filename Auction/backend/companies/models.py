from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import User

class Company(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended')
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos/')
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    managers = models.ManyToManyField(User, related_name='managed_companies')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CompanyAddress(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

class CompanyDocument(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)  # registration, tax, etc.
    document_file = models.FileField(upload_to='company_documents/')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.company.name}"

class CompanyStatistics(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    total_auctions = models.PositiveIntegerField(default=0)
    active_auctions = models.PositiveIntegerField(default=0)
    completed_auctions = models.PositiveIntegerField(default=0)
    total_bids = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

class CompanyFinanceReport(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    total_fees = models.DecimalField(max_digits=12, decimal_places=2)
    net_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_auctions = models.PositiveIntegerField()
    average_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

class CompanyNotification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
