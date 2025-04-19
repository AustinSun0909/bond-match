from django.contrib import admin
from .models import Issuer, Bond, FundCompany, Fund, Person, BondHolding, SearchHistory

@admin.register(Issuer)
class IssuerAdmin(admin.ModelAdmin):
    list_display = ('issuer_name', 'created_at', 'updated_at')
    search_fields = ('issuer_name',)

@admin.register(Bond)
class BondAdmin(admin.ModelAdmin):
    list_display = ('bond_code', 'issuer', 'issue_date', 'term_years', 'remaining_term', 'can_be_redeemed')
    search_fields = ('bond_code', 'issuer__issuer_name')
    list_filter = ('can_be_redeemed',)

@admin.register(FundCompany)
class FundCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_type', 'created_at', 'updated_at')
    search_fields = ('company_name',)
    list_filter = ('company_type',)

@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('fund_name', 'fund_company', 'fund_manager', 'contact_email', 'contact_phone')
    search_fields = ('fund_name', 'fund_company__company_name', 'fund_manager')
    list_filter = ('fund_company__company_type',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund', 'role', 'is_primary')
    search_fields = ('name', 'fund__fund_name')
    list_filter = ('role', 'is_primary')

@admin.register(BondHolding)
class BondHoldingAdmin(admin.ModelAdmin):
    list_display = ('fund', 'bond', 'purchase_date', 'remaining_term_at_purchase', 'holding_amount', 'is_current_holding')
    search_fields = ('fund__fund_name', 'bond__bond_code')
    list_filter = ('is_current_holding',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'bond_code', 'search_date')
    search_fields = ('user__username', 'bond_code')
    readonly_fields = ('search_date',)
