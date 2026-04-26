from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Investor, InvestorReport
from .serializers import InvestorReportSerializer, InvestorSerializer


class InvestorViewSet(viewsets.ModelViewSet):
	queryset = Investor.objects.all().order_by('name')
	serializer_class = InvestorSerializer
	permission_classes = [IsAuthenticated]


class InvestorReportViewSet(viewsets.ModelViewSet):
	queryset = InvestorReport.objects.all().order_by('-created_at')
	serializer_class = InvestorReportSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['post'])
	def send(self, request, pk=None):
		report = self.get_object()
		report.is_sent = True
		report.sent_date = request.data.get('sent_date') or timezone.localdate()
		report.save(update_fields=['is_sent', 'sent_date'])
		return Response(self.get_serializer(report).data)
