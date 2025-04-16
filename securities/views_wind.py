# securities/views_wind.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .wind_service import get_bond_info_by_code, get_bond_info_by_abbr
import logging

logger = logging.getLogger(__name__)

class BondInfoByAbbrView(APIView):
    """
    通过债券简称查询债券信息（包括Wind代码、发行主体、起息日和期限）。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bond_abbr = request.query_params.get("bond_abbr")
        if not bond_abbr:
            return Response({"error": "缺少参数 bond_abbr"}, status=400)
        
        data = get_bond_info_by_abbr(bond_abbr)
        if data is None:
            return Response({"error": "没有查询到相关信息或查询失败"}, status=404)
        
        return Response(data)

class BondInfoByCodeView(APIView):
    """
    通过债券Wind代码查询债券信息。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bond_code = request.query_params.get("bond_code")
        if not bond_code:
            return Response({"error": "缺少参数 bond_code"}, status=400)
        
        data = get_bond_info_by_code(bond_code)
        if data is None:
            return Response({"error": "没有查询到相关信息或查询失败"}, status=404)
        
        return Response(data)
