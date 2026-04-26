from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvestorReportViewSet, InvestorViewSet

router = DefaultRouter()
router.register('investors', InvestorViewSet)
router.register('investor-reports', InvestorReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
