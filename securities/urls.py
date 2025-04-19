# securities/urls.py
from django.urls import path
from .views import (
    SignUpView, LoginView, ForgotPasswordView, ResetPasswordView,
    BondSearchView, IssuerListView, BondDetailView, BondMatchView,
    SearchHistoryView
)

urlpatterns = [
    # Authentication endpoints
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
    # Bond-related endpoints
    path('bonds/search/', BondSearchView.as_view(), name='bond_search'),
    path('bonds/match/', BondMatchView.as_view(), name='bond_match'),
    path('issuers/', IssuerListView.as_view(), name='issuer_list'),
    path('bonds/<str:bond_code>/', BondDetailView.as_view(), name='bond_detail'),
    
    # User history
    path('search-history/', SearchHistoryView.as_view(), name='search_history'),
]
