from rest_framework import serializers
from .models import Issuer, Bond, FundCompany, Fund, Person, FundBondHolding

class IssuerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issuer
        fields = '__all__'
