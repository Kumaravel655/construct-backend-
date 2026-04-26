from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Drawing
from .serializers import DrawingSerializer


class DrawingViewSet(viewsets.ModelViewSet):
	queryset = Drawing.objects.all().order_by('-created_at')
	serializer_class = DrawingSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		project_id = self.request.query_params.get('project')
		drawing_type = self.request.query_params.get('type')

		if project_id:
			queryset = queryset.filter(project_id=project_id)
		if drawing_type:
			queryset = queryset.filter(drawing_type=drawing_type)
		return queryset

	@action(detail=True, methods=['post'])
	def approve(self, request, pk=None):
		drawing = self.get_object()
		drawing.status = 'approved'
		drawing.approved_by = request.user
		drawing.approval_date = request.data.get('approval_date') or timezone.localdate()
		drawing.save(update_fields=['status', 'approved_by', 'approval_date'])
		return Response(self.get_serializer(drawing).data)

	@action(detail=True, methods=['post'])
	def supersede(self, request, pk=None):
		drawing = self.get_object()
		new_drawing_id = request.data.get('superseded_by')
		if new_drawing_id:
			drawing.superseded_by_id = new_drawing_id
		drawing.status = 'superseded'
		drawing.save(update_fields=['superseded_by', 'status'])
		return Response(self.get_serializer(drawing).data)

	@action(detail=False, methods=['get'])
	def latest(self, request):
		latest_map = {}
		for drawing in self.get_queryset().order_by('drawing_number', '-created_at'):
			latest_map.setdefault(drawing.drawing_number, drawing)
		serializer = self.get_serializer(list(latest_map.values()), many=True)
		return Response(serializer.data)
