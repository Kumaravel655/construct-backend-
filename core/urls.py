from rest_framework import routers
from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('projects', ProjectViewSet)
router.register('tasks', TaskViewSet)
router.register('documents', DocumentViewSet)
router.register('vendors', VendorViewSet)
router.register('purchaseorders', PurchaseOrderViewSet)
router.register('budgets', BudgetViewSet)
router.register('attendance', AttendanceViewSet)
router.register('attendance-sessions', AttendanceSessionViewSet, basename='attendance-session')
router.register('daily-work-items', DailyWorkItemViewSet, basename='daily-work-item')
router.register('invoices', InvoiceViewSet)
router.register('equipment', EquipmentViewSet)
router.register('incidents', SafetyIncidentViewSet)
router.register('communications', CommunicationViewSet)
router.register('material-requests', MaterialRequestViewSet)
router.register('quality-inspections', QualityInspectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
]
