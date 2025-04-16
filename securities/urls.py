# securities/urls.py
from django.urls import path
from .views import IssuerListView
from .views_wind import BondInfoByAbbrView, BondInfoByCodeView

urlpatterns = [
    path('issuers/', IssuerListView.as_view(), name='issuer-list'),
    path('bond/byabbr/', BondInfoByAbbrView.as_view(), name='bond-info-byabbr'),
    path('bond/bycode/', BondInfoByCodeView.as_view(), name='bond-info-bycode'),
]
