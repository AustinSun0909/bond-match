# securities/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Issuer(models.Model):
    issuer_name = models.CharField(max_length=255, unique=True)
    other_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.issuer_name

class Bond(models.Model):
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, related_name='bonds')
    bond_code = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(default=timezone.now)
    term_years = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    remaining_term = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))  # Current remaining term
    can_be_redeemed = models.BooleanField(default=False)
    other_attributes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bond_code

class FundCompany(models.Model):
    COMPANY_TYPES = [
        ('FUND', 'Fund Manager'),
        ('INSURANCE', 'Insurance Company'),
        ('BANK', 'Bank'),
        ('OTHER', 'Other Financial Institution')
    ]
    
    company_name = models.CharField(max_length=255, unique=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, default='FUND')
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class Fund(models.Model):
    fund_company = models.ForeignKey(FundCompany, on_delete=models.CASCADE, related_name='funds')
    fund_name = models.CharField(max_length=255)
    fund_manager = models.CharField(max_length=255, default='Unknown')  # Primary fund manager name
    contact_email = models.EmailField(max_length=100, default='unknown@example.com')
    contact_phone = models.CharField(max_length=50, default='000-0000-0000')
    other_attributes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fund_name} ({self.fund_company.company_name})"

class Person(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='persons')
    name = models.CharField(max_length=255, default='Unknown')
    role = models.CharField(max_length=50, default='Unknown')  # 例如 '基金经理' 或 '交易员'
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)  # 用于标记重点，如曾持有过可提还债券
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

class BondHolding(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='bond_holdings')
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE, related_name='bond_holdings')
    purchase_date = models.DateField(default=timezone.now)
    remaining_term_at_purchase = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    holding_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0.00'))
    is_current_holding = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('fund', 'bond', 'purchase_date')

    def __str__(self):
        return f"{self.fund.fund_name} - {self.bond.bond_code} ({self.purchase_date})"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    bond_code = models.CharField(max_length=50, default='')
    search_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.bond_code} ({self.search_date})"
