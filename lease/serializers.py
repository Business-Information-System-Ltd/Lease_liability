from rest_framework import serializers
from .models import LeaseContract, LeaseFinancial

class LeaseFinancialSerializer(serializers.ModelSerializer):
    amortization_schedule = serializers.SerializerMethodField()
    class Meta:
        model = LeaseFinancial
        fields = '__all__'

    def get_amortization_schedule(self, obj):
        
        return obj.get_amortization_schedule()



class LeaseContractSerializer(serializers.ModelSerializer):
    
    financial = LeaseFinancialSerializer(read_only=True)
    read_only_fields = ('present_value',)
    
    class Meta:
        model = LeaseContract
        fields = '__all__'