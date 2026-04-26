from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ActionItem, Meeting, MeetingAttendee
from .serializers import ActionItemSerializer, MeetingAttendeeSerializer, MeetingSerializer


class MeetingViewSet(viewsets.ModelViewSet):
	queryset = Meeting.objects.all().order_by('-scheduled_date', '-scheduled_time')
	serializer_class = MeetingSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		meeting_type = self.request.query_params.get('type')
		if meeting_type:
			queryset = queryset.filter(meeting_type=meeting_type)
		return queryset

	@action(detail=True, methods=['post'])
	def start(self, request, pk=None):
		meeting = self.get_object()
		meeting.status = 'in_progress'
		meeting.save(update_fields=['status'])
		return Response(self.get_serializer(meeting).data)

	@action(detail=True, methods=['post'])
	def complete(self, request, pk=None):
		meeting = self.get_object()
		meeting.status = 'completed'
		meeting.actual_date = request.data.get('actual_date') or timezone.localdate()
		meeting.minutes = request.data.get('minutes', meeting.minutes)
		meeting.save(update_fields=['status', 'actual_date', 'minutes'])
		return Response(self.get_serializer(meeting).data)

	@action(detail=False, methods=['get'])
	def today(self, request):
		queryset = self.get_queryset().filter(scheduled_date=timezone.localdate())
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)


class MeetingAttendeeViewSet(viewsets.ModelViewSet):
	queryset = MeetingAttendee.objects.all().order_by('meeting_id', 'id')
	serializer_class = MeetingAttendeeSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['patch'], url_path='mark-present')
	def mark_present(self, request, pk=None):
		attendee = self.get_object()
		attendee.is_present = True
		attendee.remarks = request.data.get('remarks', attendee.remarks)
		attendee.save(update_fields=['is_present', 'remarks'])
		return Response(self.get_serializer(attendee).data)


class ActionItemViewSet(viewsets.ModelViewSet):
	queryset = ActionItem.objects.all().order_by('-due_date')
	serializer_class = ActionItemSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		assignee = self.request.query_params.get('assignee')
		if assignee:
			queryset = queryset.filter(assigned_to_id=assignee)
		return queryset

	@action(detail=True, methods=['patch'])
	def complete(self, request, pk=None):
		action_item = self.get_object()
		action_item.status = 'done'
		action_item.completion_date = request.data.get('completion_date') or timezone.localdate()
		action_item.remarks = request.data.get('remarks', action_item.remarks)
		action_item.save(update_fields=['status', 'completion_date', 'remarks'])
		return Response(self.get_serializer(action_item).data)

	@action(detail=False, methods=['get'])
	def overdue(self, request):
		queryset = self.get_queryset().filter(due_date__lt=timezone.localdate()).exclude(status='done')
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)
