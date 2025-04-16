# securities/models.py
from django.db import models

class Issuer(models.Model):
    issuer_name = models.CharField(max_length=255)
    other_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.issuer_name

class Bond(models.Model):
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, related_name='bonds')
    bond_code = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    term_years = models.DecimalField(max_digits=4, decimal_places=2)
    can_be_redeemed = models.BooleanField(default=False)  # True 表示债券是可提还的
    other_attributes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.bond_code

class FundCompany(models.Model):
    company_name = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class Fund(models.Model):
    fund_company = models.ForeignKey(FundCompany, on_delete=models.CASCADE, related_name='funds')
    fund_name = models.CharField(max_length=255)
    other_attributes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fund_name

class Person(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='persons')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50)  # 例如 '基金经理' 或 '交易员'
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=False)  # 用于标记重点，如曾持有过可提还债券

    def __str__(self):
        return f"{self.name} ({self.role})"

class FundBondHolding(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='bond_holdings')
    bond = models.ForeignKey(Bond, on_delete=models.CASCADE, related_name='bond_holdings')
    report_date = models.DateField()
    holding_amount = models.DecimalField(max_digits=18, decimal_places=2)

    def __str__(self):
        return f"{self.fund.fund_name} 持有 {self.bond.bond_code}"
