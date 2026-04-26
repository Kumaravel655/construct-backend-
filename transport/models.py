from django.conf import settings
from django.db import models


class Vehicle(models.Model):
	VEHICLE_TYPES = [
		('tipper_truck', 'Tipper Truck'),
		('excavator', 'Excavator'),
		('jcb', 'JCB'),
		('concrete_mixer', 'Concrete Mixer'),
		('crane', 'Crane'),
		('roller', 'Road Roller'),
		('other', 'Other'),
	]

	STATUS_CHOICES = [
		('available', 'Available'),
		('in_use', 'In Use'),
		('maintenance', 'Under Maintenance'),
		('breakdown', 'Breakdown'),
		('inactive', 'Inactive'),
	]

	vehicle_id = models.CharField(max_length=50, unique=True)
	registration_number = models.CharField(max_length=30, unique=True)
	vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPES)
	make = models.CharField(max_length=100)
	model = models.CharField(max_length=100)
	year = models.IntegerField()
	current_project = models.ForeignKey('core.Project', on_delete=models.SET_NULL, null=True, blank=True)
	assigned_driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
	last_service_date = models.DateField(null=True, blank=True)
	next_service_date = models.DateField(null=True, blank=True)
	insurance_expiry = models.DateField(null=True, blank=True)
	fitness_expiry = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"{self.vehicle_id} - {self.registration_number}"


class TripSheet(models.Model):
	STATUS_CHOICES = [
		('open', 'Open'),
		('completed', 'Completed'),
		('verified', 'Verified'),
	]

	trip_id = models.CharField(max_length=50, unique=True)
	vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
	driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='trips')
	project = models.ForeignKey('core.Project', on_delete=models.PROTECT)
	trip_date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField(null=True, blank=True)
	start_odometer = models.DecimalField(max_digits=10, decimal_places=1)
	end_odometer = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
	from_location = models.CharField(max_length=200)
	to_location = models.CharField(max_length=200)
	purpose = models.TextField()
	material_carried = models.CharField(max_length=200, blank=True)
	quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	unit = models.CharField(max_length=20, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
	verified_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='verified_trips',
	)
	notes = models.TextField(blank=True)

	@property
	def distance_km(self):
		if self.end_odometer is None:
			return None
		return self.end_odometer - self.start_odometer

	def __str__(self):
		return self.trip_id


class FuelLog(models.Model):
	FUEL_TYPES = [('diesel', 'Diesel'), ('petrol', 'Petrol')]

	vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
	driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	project = models.ForeignKey('core.Project', on_delete=models.PROTECT)
	fill_date = models.DateField()
	fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
	quantity_litres = models.DecimalField(max_digits=8, decimal_places=2)
	rate_per_litre = models.DecimalField(max_digits=6, decimal_places=2)
	odometer_reading = models.DecimalField(max_digits=10, decimal_places=1)
	fuel_station = models.CharField(max_length=200)
	bill_number = models.CharField(max_length=100, blank=True)
	bill_attachment = models.FileField(upload_to='fuel_bills/', blank=True)
	approved_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='approved_fuel_logs',
	)

	@property
	def total_cost(self):
		return self.quantity_litres * self.rate_per_litre

	def __str__(self):
		return f"{self.vehicle.vehicle_id} - {self.fill_date}"
