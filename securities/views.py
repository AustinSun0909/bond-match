# securities/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Issuer
from .serializers import IssuerSerializer

class IssuerListView(APIView):
    # 需要认证的用户才能访问
    permission_classes = [IsAuthenticated]

    def get(self, request):
        issuers = Issuer.objects.all()
        serializer = IssuerSerializer(issuers, many=True)
        return Response(serializer.data)
