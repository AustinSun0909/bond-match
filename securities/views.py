# securities/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .models import Issuer, Bond, Fund, BondHolding, SearchHistory, Person
from .serializers import IssuerSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.db.models import Q
from decimal import Decimal
from .wind_service import get_bond_info_by_code, get_bond_info_by_abbr
import uuid
import datetime

# Store password reset tokens temporarily
# In production, this should be in a database
password_reset_tokens = {}

class IssuerListView(APIView):
    # 需要认证的用户才能访问
    permission_classes = [IsAuthenticated]

    def get(self, request):
        issuers = Issuer.objects.all()
        serializer = IssuerSerializer(issuers, many=True)
        return Response(serializer.data)

WECHAT_APP_ID = 'YOUR_APP_ID'  # Replace with your WeChat App ID
WECHAT_APP_SECRET = 'YOUR_APP_SECRET'  # Replace with your WeChat App Secret

@csrf_exempt
def wechat_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            
            if not code:
                return JsonResponse({'error': 'No code provided'}, status=400)

            # Exchange code for access token
            token_url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}&code={code}&grant_type=authorization_code'
            response = requests.get(token_url)
            token_data = response.json()

            if 'errcode' in token_data:
                return JsonResponse({'error': 'Failed to get access token'}, status=400)

            # Get user info
            user_info_url = f'https://api.weixin.qq.com/sns/userinfo?access_token={token_data["access_token"]}&openid={token_data["openid"]}'
            user_response = requests.get(user_info_url)
            user_data = user_response.json()

            if 'errcode' in user_data:
                return JsonResponse({'error': 'Failed to get user info'}, status=400)

            # Here you would typically:
            # 1. Create or update user in your database
            # 2. Generate a JWT token for your application
            # 3. Return the token to the frontend

            # For now, we'll just return a success message
            return JsonResponse({
                'success': True,
                'token': 'your_jwt_token_here',  # Replace with actual JWT token
                'user': {
                    'openid': user_data.get('openid'),
                    'nickname': user_data.get('nickname'),
                    'headimgurl': user_data.get('headimgurl')
                }
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

class BondInfoByCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bond_code = request.query_params.get("bond_code")
        if not bond_code:
            return Response({"error": "Bond code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_bond_info_by_code(bond_code)
        if data is None:
            return Response({"error": "Bond not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(data)

class BondInfoByAbbrView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bond_abbr = request.query_params.get("bond_abbr")
        if not bond_abbr:
            return Response({"error": "Bond abbreviation is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = get_bond_info_by_abbr(bond_abbr)
        if data is None:
            return Response({"error": "Bond not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(data)

class BondMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        bond_code = request.data.get('bond_code')
        if not bond_code:
            return Response(
                {'error': 'Bond code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get bond info from mock Wind service
        bond_info = get_bond_info_by_code(bond_code)
        if not bond_info:
            return Response(
                {'error': 'Failed to get bond information'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find potential buyers based on issuer
        issuer_name = bond_info['issuer']

        # Query funds that have previously held bonds from the same issuer
        potential_buyers = BondHolding.objects.filter(
            bond__issuer__issuer_name=issuer_name
        ).select_related('fund', 'fund__fund_company').distinct()

        # Format the results
        results = []
        for holding in potential_buyers:
            # Get all persons (fund managers and traders) for this fund
            persons = Person.objects.filter(fund=holding.fund).values(
                'name', 'role', 'phone', 'email'
            )
            
            # Get primary fund manager's contact info
            primary_manager = persons.filter(is_primary=True).first()
            
            result = {
                'company_name': holding.fund.fund_company.company_name,
                'fund_name': holding.fund.fund_name,
                'fund_manager': holding.fund.fund_manager,
                'primary_manager_contact': {
                    'phone': primary_manager.get('phone') if primary_manager else None,
                    'email': primary_manager.get('email') if primary_manager else None
                } if primary_manager else None,
                'all_contacts': list(persons)
            }
            results.append(result)

        # Save search history (only bond code)
        SearchHistory.objects.create(
            user=request.user,
            bond_code=bond_code
        )

        if not results:
            return Response({
                'message': '数据库中未找到曾持有该债券主体所发行债券之基金、理财等潜在买家。',
                'bond_info': bond_info
            })

        return Response({
            'bond_info': bond_info,
            'potential_buyers': results
        })

class SearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = SearchHistory.objects.filter(
            user=request.user
        ).order_by('-search_date')[:10]  # Get last 10 searches

        results = []
        for entry in history:
            results.append({
                'bond_code': entry.bond_code,
                'search_date': entry.search_date.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Response(results)

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user with provided credentials
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email if email else ''  # Make email optional
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username
            }
        })

class ForgotPasswordView(APIView):
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            # Generate a unique token
            token = str(uuid.uuid4())
            # Store token with timestamp (valid for 1 hour)
            password_reset_tokens[token] = {
                'user_id': user.id,
                'timestamp': datetime.datetime.now()
            }
            
            # Send email with reset link
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
            send_mail(
                'Password Reset - Bond Match',
                f'Click the following link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({"message": "Password reset email sent"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Don't reveal that email doesn't exist for security reasons
            return Response({"message": "Password reset email sent if account exists"}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = []
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('newPassword')
        
        if not token or not new_password:
            return Response({"error": "Token and new password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token
        token_data = password_reset_tokens.get(token)
        if not token_data:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token is expired (1 hour)
        token_time = token_data['timestamp']
        if (datetime.datetime.now() - token_time).total_seconds() > 3600:
            # Remove expired token
            password_reset_tokens.pop(token)
            return Response({"error": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get user and set new password
            user = User.objects.get(id=token_data['user_id'])
            user.set_password(new_password)
            user.save()
            
            # Remove used token
            password_reset_tokens.pop(token)
            
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

class BondSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')
        if not query or len(query) < 2:  # Require at least 2 characters
            return Response(
                {'error': 'Please provide a valid search query (at least 2 characters)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Search for bonds by code, attributes containing name, or issuer name
        bonds = Bond.objects.filter(
            Q(bond_code__icontains=query) | 
            Q(other_attributes__icontains=query) | 
            Q(issuer__issuer_name__icontains=query)
        ).select_related('issuer')[:50]  # Limit to 50 results

        if not bonds:
            # No results found
            return Response({'results': []})

        # Format the results
        results = []
        for bond in bonds:
            # Extract bond name from other_attributes if available
            bond_name = "Unknown"
            if bond.other_attributes and "Name:" in bond.other_attributes:
                try:
                    bond_name = bond.other_attributes.split("Name:")[1].strip()
                except:
                    pass
                
            # Extract bond type from other_attributes if available
            bond_type = "Unknown"
            if bond.other_attributes and "Bond type:" in bond.other_attributes:
                try:
                    bond_type = bond.other_attributes.split("Bond type:")[1].split(",")[0].strip()
                except:
                    pass
                
            results.append({
                'id': bond.id,
                'bond_code': bond.bond_code,
                'bond_name': bond_name,
                'issuer': bond.issuer.issuer_name,
                'coupon_rate': f"{bond.term_years}年",  # Display term years instead of coupon rate
                'maturity_date': bond.issue_date.strftime('%Y-%m-%d')
            })

        # Save search history
        SearchHistory.objects.create(
            user=request.user,
            bond_code=query
        )

        return Response({'results': results})

class BondDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, bond_code):
        try:
            # Get bond data from Wind service
            bond_data = get_bond_info_by_code(bond_code)
            
            if not bond_data:
                return Response(
                    {'error': 'Bond not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Try to get bond holdings information
            try:
                bond = Bond.objects.get(bond_code=bond_code)
                # Get all holdings for this bond
                holdings = BondHolding.objects.filter(bond=bond).select_related('fund', 'fund__fund_company')
                
                buyers = []
                for holding in holdings:
                    buyers.append({
                        'fund_name': holding.fund.fund_name,
                        'company_name': holding.fund.fund_company.company_name,
                        'holding_amount': holding.holding_amount,
                        'holding_percentage': holding.holding_percentage
                    })
                
                bond_data['holders'] = buyers
            except Bond.DoesNotExist:
                # If the bond is not in our database, just return the Wind data
                bond_data['holders'] = []
            
            # Record this view in search history
            SearchHistory.objects.create(
                user=request.user,
                bond_code=bond_code
            )
            
            return Response(bond_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving bond details: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
