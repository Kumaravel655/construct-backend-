from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import GovernmentContact, GovernmentDepartment, TenderApplication
from .serializers import (
	GovernmentContactSerializer,
	GovernmentDepartmentSerializer,
	TenderApplicationSerializer,
)


class GovernmentDepartmentViewSet(viewsets.ModelViewSet):
	queryset = GovernmentDepartment.objects.all().order_by('name')
	serializer_class = GovernmentDepartmentSerializer
	permission_classes = [IsAuthenticated]


class TenderApplicationViewSet(viewsets.ModelViewSet):
	queryset = TenderApplication.objects.all().order_by('-created_at')
	serializer_class = TenderApplicationSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['post'])
	def approve(self, request, pk=None):
		tender = self.get_object()
		tender.status = 'approved'
		tender.decision_date = request.data.get('decision_date') or tender.decision_date
		tender.save(update_fields=['status', 'decision_date'])
		return Response(self.get_serializer(tender).data)

	@action(detail=True, methods=['post'])
	def submit(self, request, pk=None):
		tender = self.get_object()
		if tender.status != 'draft':
			return Response({'error': 'Only draft tenders can be submitted'}, status=status.HTTP_400_BAD_REQUEST)
		tender.status = 'submitted'
		tender.save(update_fields=['status'])
		return Response(self.get_serializer(tender).data)


class GovernmentContactViewSet(viewsets.ModelViewSet):
	queryset = GovernmentContact.objects.all().order_by('officer_name')
	serializer_class = GovernmentContactSerializer
	permission_classes = [IsAuthenticated]
