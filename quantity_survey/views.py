from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.exports import export_rows_to_excel

from .models import BOQ, BOQItem, MeasurementBook, MeasurementEntry
from .serializers import BOQItemSerializer, BOQSerializer, MeasurementBookSerializer, MeasurementEntrySerializer


class BOQViewSet(viewsets.ModelViewSet):
	queryset = BOQ.objects.all().order_by('-created_at')
	serializer_class = BOQSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['post'])
	def approve(self, request, pk=None):
		boq = self.get_object()
		boq.is_approved = True
		boq.approved_by = request.user
		boq.save(update_fields=['is_approved', 'approved_by'])
		return Response(self.get_serializer(boq).data)

	@action(detail=True, methods=['get'])
	def items(self, request, pk=None):
		boq = self.get_object()
		serializer = BOQItemSerializer(boq.items.all().order_by('id'), many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['post'], url_path='export-excel')
	def export_excel(self, request, pk=None):
		boq = self.get_object()
		headers = ['Item Code', 'Description', 'Unit', 'Quantity', 'Unit Rate', 'Amount']
		rows = [
			[item.item_code, item.description, item.unit, item.quantity, item.unit_rate, item.amount]
			for item in boq.items.all().order_by('id')
		]
		return export_rows_to_excel(f'boq_{boq.boq_id}.xlsx', headers, rows)


class BOQItemViewSet(viewsets.ModelViewSet):
	queryset = BOQItem.objects.all().order_by('id')
	serializer_class = BOQItemSerializer
	permission_classes = [IsAuthenticated]


class MeasurementBookViewSet(viewsets.ModelViewSet):
	queryset = MeasurementBook.objects.all().order_by('-measurement_date')
	serializer_class = MeasurementBookSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['post'])
	def verify(self, request, pk=None):
		mb = self.get_object()
		mb.is_verified = True
		mb.verified_by = request.user
		mb.save(update_fields=['is_verified', 'verified_by'])
		return Response(self.get_serializer(mb).data)

	@action(detail=True, methods=['get'])
	def entries(self, request, pk=None):
		mb = self.get_object()
		serializer = MeasurementEntrySerializer(mb.entries.all().order_by('id'), many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['post'], url_path='export-pdf')
	def export_pdf(self, request, pk=None):
		mb = self.get_object()
		return Response(
			{'message': 'PDF export endpoint is ready for integration', 'measurement_book': mb.mb_number}
		)


class MeasurementEntryViewSet(viewsets.ModelViewSet):
	queryset = MeasurementEntry.objects.all().order_by('id')
	serializer_class = MeasurementEntrySerializer
	permission_classes = [IsAuthenticated]
