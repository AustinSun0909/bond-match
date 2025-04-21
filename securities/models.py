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
    bond_name = models.CharField(max_length=255, default='')  # Added bond_name field
    issue_date = models.DateField(default=timezone.now)
    maturity_date = models.DateField(null=True, blank=True)  # Added maturity date
    coupon_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Added coupon rate
    term_years = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    remaining_term = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))  # Current remaining term
    can_be_redeemed = models.BooleanField(default=False)
    other_attributes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bond_code} - {self.bond_name}"

class FundCompany(models.Model):
    COMPANY_TYPES = [
        ('FUND', '基金公司'),
        ('WEALTH', '理财公司'),
        ('BROKER', '券商自营'),
        ('INSURANCE', '保险公司'),
        ('BANK', '银行'),
        ('OTHER', '其他金融机构')
    ]
    
    company_name = models.CharField(max_length=255, unique=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, default='FUND')
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)
    aum = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0.00'), help_text='Assets under management')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class Person(models.Model):
    """Contact person for a fund company or a specific fund"""
    company = models.ForeignKey(FundCompany, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    fund = models.ForeignKey('Fund', on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    name = models.CharField(max_length=255, default='Unknown')
    role = models.CharField(max_length=50, default='Unknown')  # 例如 '基金经理' 或 '交易员'
    phone = models.CharField(max_length=50, blank=True, null=True)  # 工作电话
    mobile = models.CharField(max_length=50, blank=True, null=True)  # 手机号
    email = models.EmailField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)  # 用于标记是否是主要联系人
    is_leader = models.BooleanField(default=False)  # 是否是领导
    qq = models.CharField(max_length=50, blank=True, null=True)  # QQ号
    qt = models.CharField(max_length=50, blank=True, null=True)  # QT号
    wechat = models.CharField(max_length=50, blank=True, null=True)  # 微信号
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(company__isnull=False) | models.Q(fund__isnull=False),
                name='person_must_belong_to_either_company_or_fund'
            )
        ]

    def __str__(self):
        entity = self.fund.fund_name if self.fund else self.company.company_name
        return f"{self.name} ({self.role}) - {entity}"

class Fund(models.Model):
    fund_company = models.ForeignKey(FundCompany, on_delete=models.CASCADE, related_name='funds')
    fund_name = models.CharField(max_length=255)
    fund_manager = models.CharField(max_length=255, default='Unknown')  # Primary fund manager name
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    other_attributes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fund_name} ({self.fund_company.company_name})"

class BondHolding(models.Model):
    """Track bond holdings for both funds and companies directly"""
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='bond_holdings', null=True, blank=True)
    company = models.ForeignKey(FundCompany, on_delete=models.CASCADE, related_name='direct_bond_holdings', null=True, blank=True)
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE, related_name='bond_holdings')
    purchase_date = models.DateField(default=timezone.now)
    sell_date = models.DateField(null=True, blank=True)  # Date when the bond was sold, if applicable
    remaining_term_at_purchase = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    holding_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0.00'))
    holding_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'), help_text='Percentage of assets')
    is_current_holding = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(fund__isnull=False) | models.Q(company__isnull=False),
                name='holding_must_belong_to_either_fund_or_company'
            )
        ]

    def __str__(self):
        owner = self.fund.fund_name if self.fund else self.company.company_name
        status = "Current" if self.is_current_holding else f"Sold on {self.sell_date}"
        return f"{owner} - {self.bond.bond_code} ({status})"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255, default='')  # Default empty string for existing records
    bond_code = models.CharField(max_length=50, blank=True, null=True)  # If the search resulted in a specific bond
    bond_name = models.CharField(max_length=255, blank=True, null=True)  # Bond name if available
    result_count = models.IntegerField(default=0)  # Number of results returned
    search_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.query} ({self.search_date})"
