from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FundAllotmentViewSet, FundSourceViewSet, FundSummaryView, FundTransactionViewSet

router = DefaultRouter()
router.register('fund-sources', FundSourceViewSet)
router.register('fund-allotments', FundAllotmentViewSet)
router.register('fund-transactions', FundTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('fund-summary/', FundSummaryView.as_view(), name='fund-summary'),
]
