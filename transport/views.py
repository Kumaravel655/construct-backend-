from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exports import export_rows_to_excel

from .models import FuelLog, TripSheet, Vehicle
from .serializers import FuelLogSerializer, TripSheetSerializer, VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
	queryset = Vehicle.objects.all().order_by('vehicle_id')
	serializer_class = VehicleSerializer
	permission_classes = [IsAuthenticated]

	@action(detail=True, methods=['post'])
	def assign(self, request, pk=None):
		vehicle = self.get_object()
		project_id = request.data.get('project')
		driver_id = request.data.get('driver')
		if not project_id or not driver_id:
			return Response({'error': 'project and driver are required'}, status=status.HTTP_400_BAD_REQUEST)
		vehicle.current_project_id = project_id
		vehicle.assigned_driver_id = driver_id
		vehicle.status = 'in_use'
		vehicle.save(update_fields=['current_project', 'assigned_driver', 'status'])
		return Response(self.get_serializer(vehicle).data)

	@action(detail=True, methods=['post'])
	def maintenance(self, request, pk=None):
		vehicle = self.get_object()
		vehicle.status = 'maintenance'
		vehicle.last_service_date = request.data.get('last_service_date') or timezone.localdate()
		vehicle.next_service_date = request.data.get('next_service_date') or vehicle.next_service_date
		vehicle.save(update_fields=['status', 'last_service_date', 'next_service_date'])
		return Response(self.get_serializer(vehicle).data)

	@action(detail=False, methods=['get'], url_path='due-maintenance')
	def due_maintenance(self, request):
		today = timezone.localdate()
		queryset = Vehicle.objects.filter(next_service_date__isnull=False, next_service_date__lte=today).order_by(
			'next_service_date'
		)
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)


class TripSheetViewSet(viewsets.ModelViewSet):
	queryset = TripSheet.objects.all().order_by('-trip_date', '-id')
	serializer_class = TripSheetSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		vehicle_id = self.request.query_params.get('vehicle')
		driver_id = self.request.query_params.get('driver')
		project_id = self.request.query_params.get('project')
		trip_date = self.request.query_params.get('date')

		if vehicle_id:
			queryset = queryset.filter(vehicle_id=vehicle_id)
		if driver_id:
			queryset = queryset.filter(driver_id=driver_id)
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		if trip_date:
			queryset = queryset.filter(trip_date=trip_date)
		return queryset

	@action(detail=True, methods=['patch'])
	def complete(self, request, pk=None):
		trip = self.get_object()
		trip.end_time = request.data.get('end_time') or trip.end_time
		trip.end_odometer = request.data.get('end_odometer') or trip.end_odometer
		trip.notes = request.data.get('notes', trip.notes)
		trip.status = 'completed'
		trip.save(update_fields=['end_time', 'end_odometer', 'notes', 'status'])
		return Response(self.get_serializer(trip).data)

	@action(detail=True, methods=['patch'])
	def verify(self, request, pk=None):
		trip = self.get_object()
		trip.status = 'verified'
		trip.verified_by = request.user
		trip.save(update_fields=['status', 'verified_by'])
		return Response(self.get_serializer(trip).data)

	@action(detail=False, methods=['get'], url_path='export-excel')
	def export_excel(self, request):
		queryset = self.get_queryset().select_related('vehicle', 'driver', 'project', 'verified_by')
		headers = [
			'Trip ID',
			'Date',
			'Vehicle',
			'Driver',
			'Project',
			'From',
			'To',
			'Purpose',
			'Start Odometer',
			'End Odometer',
			'Distance',
			'Status',
			'Verified By',
		]
		rows = [
			[
				obj.trip_id,
				obj.trip_date,
				obj.vehicle.vehicle_id,
				obj.driver.username,
				obj.project.name,
				obj.from_location,
				obj.to_location,
				obj.purpose,
				obj.start_odometer,
				obj.end_odometer,
				obj.distance_km,
				obj.status,
				obj.verified_by.username if obj.verified_by else '',
			]
			for obj in queryset
		]
		return export_rows_to_excel('trip_sheets.xlsx', headers, rows)


class FuelLogViewSet(viewsets.ModelViewSet):
	queryset = FuelLog.objects.all().order_by('-fill_date', '-id')
	serializer_class = FuelLogSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		vehicle_id = self.request.query_params.get('vehicle')
		project_id = self.request.query_params.get('project')

		if vehicle_id:
			queryset = queryset.filter(vehicle_id=vehicle_id)
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		return queryset

	@action(detail=False, methods=['get'], url_path='export-excel')
	def export_excel(self, request):
		queryset = self.get_queryset().select_related('vehicle', 'driver', 'project', 'approved_by')
		headers = [
			'Date',
			'Vehicle',
			'Driver',
			'Project',
			'Fuel Type',
			'Quantity Litres',
			'Rate/Litre',
			'Total Cost',
			'Odometer',
			'Fuel Station',
			'Bill Number',
			'Approved By',
		]
		rows = [
			[
				obj.fill_date,
				obj.vehicle.vehicle_id,
				obj.driver.username,
				obj.project.name,
				obj.fuel_type,
				obj.quantity_litres,
				obj.rate_per_litre,
				obj.total_cost,
				obj.odometer_reading,
				obj.fuel_station,
				obj.bill_number,
				obj.approved_by.username if obj.approved_by else '',
			]
			for obj in queryset
		]
		return export_rows_to_excel('fuel_logs.xlsx', headers, rows)


class FuelSummaryView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		project_id = request.query_params.get('project')
		queryset = FuelLog.objects.all()
		if project_id:
			queryset = queryset.filter(project_id=project_id)
		summary = queryset.aggregate(total_litres=Sum('quantity_litres'))
		total_cost = sum(item.total_cost for item in queryset)
		return Response({'total_litres': summary.get('total_litres') or 0, 'total_cost': total_cost})
