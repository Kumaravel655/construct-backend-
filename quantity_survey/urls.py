from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BOQItemViewSet, BOQViewSet, MeasurementBookViewSet, MeasurementEntryViewSet

router = DefaultRouter()
router.register('boqs', BOQViewSet)
router.register('boq-items', BOQItemViewSet)
router.register('measurement-books', MeasurementBookViewSet)
router.register('measurement-entries', MeasurementEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
