from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ComparativeStatement, RateAnalysis, TenderEstimate
from .serializers import ComparativeStatementSerializer, RateAnalysisSerializer, TenderEstimateSerializer


class RateAnalysisViewSet(viewsets.ModelViewSet):
	queryset = RateAnalysis.objects.all().order_by('item_code')
	serializer_class = RateAnalysisSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=False, methods=['get'])
	def schedule(self, request):
		grouped = {}
		for item in self.get_queryset():
			key = item.reference_schedule or 'Unspecified'
			grouped.setdefault(key, []).append(self.get_serializer(item).data)
		return Response(grouped)


class TenderEstimateViewSet(viewsets.ModelViewSet):
	queryset = TenderEstimate.objects.all().order_by('-prepared_date')
	serializer_class = TenderEstimateSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['post'], url_path='export-pdf')
	def export_pdf(self, request, pk=None):
		estimate = self.get_object()
		return Response({'message': 'PDF export endpoint is ready for integration', 'estimate_id': estimate.id})


class ComparativeStatementViewSet(viewsets.ModelViewSet):
	queryset = ComparativeStatement.objects.all().order_by('-comparison_date')
	serializer_class = ComparativeStatementSerializer
	permission_classes = [IsAuthenticated]
