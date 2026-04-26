from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ActionItemViewSet, MeetingAttendeeViewSet, MeetingViewSet

router = DefaultRouter()
router.register('meetings', MeetingViewSet)
router.register('meeting-attendees', MeetingAttendeeViewSet)
router.register('action-items', ActionItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
