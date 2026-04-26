from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DailyWorkReportViewSet, WorkStatusSummaryView

router = DefaultRouter()
router.register('daily-reports', DailyWorkReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('work-status-summary/', WorkStatusSummaryView.as_view(), name='work-status-summary'),
]
