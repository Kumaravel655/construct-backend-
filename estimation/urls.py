from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ComparativeStatementViewSet, RateAnalysisViewSet, TenderEstimateViewSet

router = DefaultRouter()
router.register('rate-analysis', RateAnalysisViewSet)
router.register('tender-estimates', TenderEstimateViewSet)
router.register('comparative-statements', ComparativeStatementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
