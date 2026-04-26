from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FundAllotment, FundSource, FundTransaction
from .serializers import FundAllotmentSerializer, FundSourceSerializer, FundTransactionSerializer


class FundSourceViewSet(viewsets.ModelViewSet):
	queryset = FundSource.objects.all().order_by('name')
	serializer_class = FundSourceSerializer
	permission_classes = [IsAuthenticated]


class FundAllotmentViewSet(viewsets.ModelViewSet):
	queryset = FundAllotment.objects.all().order_by('-allotment_date')
	serializer_class = FundAllotmentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		project_id = self.request.query_params.get('project')
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		return queryset

	@action(detail=True, methods=['post'])
	def release(self, request, pk=None):
		allotment = self.get_object()
		release_amount_raw = request.data.get('release_amount')
		if release_amount_raw is None:
			return Response({'error': 'release_amount is required'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			release_amount = Decimal(str(release_amount_raw))
		except (InvalidOperation, TypeError):
			return Response({'error': 'release_amount must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

		if release_amount <= 0:
			return Response({'error': 'release_amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
		if release_amount > allotment.pending_release:
			return Response({'error': 'release_amount exceeds pending release'}, status=status.HTTP_400_BAD_REQUEST)

		allotment.released_amount = allotment.released_amount + release_amount
		allotment.release_date = request.data.get('release_date') or allotment.release_date
		allotment.save(update_fields=['released_amount', 'release_date'])

		FundTransaction.objects.create(
			allotment=allotment,
			transaction_type='release',
			amount=release_amount,
			transaction_date=request.data.get('release_date') or allotment.allotment_date,
			reference_number=request.data.get('reference_number', ''),
			processed_by=request.user,
			notes=request.data.get('notes', ''),
		)
		return Response(self.get_serializer(allotment).data)


class FundTransactionViewSet(viewsets.ModelViewSet):
	queryset = FundTransaction.objects.all().order_by('-transaction_date')
	serializer_class = FundTransactionSerializer
	permission_classes = [IsAuthenticated]


class FundSummaryView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		source_summary = FundSource.objects.aggregate(
			sanctioned=Sum('sanctioned_amount'), disbursed=Sum('disbursed_amount'), repaid=Sum('repaid_amount')
		)
		allotment_summary = FundAllotment.objects.aggregate(
			allotted=Sum('allotted_amount'), released=Sum('released_amount')
		)
		return Response(
			{
				'fund_source_summary': source_summary,
				'fund_allotment_summary': allotment_summary,
			}
		)
