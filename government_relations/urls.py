from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GovernmentContactViewSet, GovernmentDepartmentViewSet, TenderApplicationViewSet

router = DefaultRouter()
router.register('government-departments', GovernmentDepartmentViewSet)
router.register('tenders', TenderApplicationViewSet)
router.register('government-contacts', GovernmentContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
