# securities/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Issuer, Bond, Fund, BondHolding, SearchHistory, Person
from .serializers import IssuerSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.db.models import Q
from decimal import Decimal
from rest_framework import status
from .wind_service import get_bond_info_by_code, get_bond_info_by_abbr

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
