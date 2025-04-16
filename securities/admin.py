from django.contrib import admin
from .models import Issuer, Bond, FundCompany, Fund, Person, FundBondHolding

admin.site.register(Issuer)
admin.site.register(Bond)
admin.site.register(FundCompany)
admin.site.register(Fund)
admin.site.register(Person)
admin.site.register(FundBondHolding)
