from rest_framework import viewsets
from rest_framework import serializers

from .models import LeaseContract, LeaseFinancial
from .serializers import LeaseContractSerializer, LeaseFinancialSerializer

class LeaseContractViewSet(viewsets.ModelViewSet):
    queryset = LeaseContract.objects.all()
    serializer_class = LeaseContractSerializer

class LeaseFinancialViewSet(viewsets.ModelViewSet):
    present_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    queryset = LeaseFinancial.objects.all()
    serializer_class = LeaseFinancialSerializer


