from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaseContractViewSet, LeaseFinancialViewSet

router = DefaultRouter()
router.register(r'leases-contracts', LeaseContractViewSet, basename='leasecontract')
router.register(r'leases-financials', LeaseFinancialViewSet, basename='leasefinancial')


urlpatterns = [
    path('', include(router.urls)),
]
