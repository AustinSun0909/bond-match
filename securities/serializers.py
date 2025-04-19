from rest_framework import serializers
from .models import Issuer, Bond, FundCompany, Fund, Person, BondHolding, SearchHistory

class IssuerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issuer
        fields = '__all__'

class BondSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bond
        fields = '__all__'

class FundCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = FundCompany
        fields = '__all__'

class FundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fund
        fields = '__all__'

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class BondHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BondHolding
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'
