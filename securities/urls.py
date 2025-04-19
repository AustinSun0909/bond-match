# securities/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('issuers/', views.IssuerListView.as_view(), name='issuer-list'),
    path('bond/match/', views.BondMatchView.as_view(), name='bond-match'),
    path('search/history/', views.SearchHistoryView.as_view(), name='search-history'),
    path('bond/bycode/', views.BondInfoByCodeView.as_view(), name='bond-info-bycode'),
    path('bond/byabbr/', views.BondInfoByAbbrView.as_view(), name='bond-info-byabbr'),
]
