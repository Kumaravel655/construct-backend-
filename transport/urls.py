from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FuelLogViewSet, FuelSummaryView, TripSheetViewSet, VehicleViewSet

router = DefaultRouter()
router.register('vehicles', VehicleViewSet)
router.register('trip-sheets', TripSheetViewSet)
router.register('fuel-logs', FuelLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('fuel-summary/', FuelSummaryView.as_view(), name='fuel-summary'),
]
