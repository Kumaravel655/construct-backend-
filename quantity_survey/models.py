from django.conf import settings
from django.db import models


class BOQ(models.Model):
	boq_id = models.CharField(max_length=50, unique=True)
	project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	version = models.CharField(max_length=10, default='1.0')
	prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	approved_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='approved_boqs',
	)
	is_approved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	notes = models.TextField(blank=True)

	def __str__(self):
		return self.boq_id


class BOQItem(models.Model):
	boq = models.ForeignKey(BOQ, on_delete=models.CASCADE, related_name='items')
	item_code = models.CharField(max_length=30)
	description = models.TextField()
	unit = models.CharField(max_length=20)
	quantity = models.DecimalField(max_digits=12, decimal_places=3)
	unit_rate = models.DecimalField(max_digits=12, decimal_places=2)
	task = models.ForeignKey('core.Task', on_delete=models.SET_NULL, null=True, blank=True)

	@property
	def amount(self):
		return self.quantity * self.unit_rate

	def __str__(self):
		return f"{self.item_code} ({self.boq.boq_id})"


class MeasurementBook(models.Model):
	mb_number = models.CharField(max_length=50, unique=True)
	project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
	boq = models.ForeignKey(BOQ, on_delete=models.PROTECT)
	measurement_date = models.DateField()
	work_description = models.TextField()
	measured_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	verified_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='verified_measurement_books',
	)
	is_verified = models.BooleanField(default=False)

	def __str__(self):
		return self.mb_number


class MeasurementEntry(models.Model):
	measurement_book = models.ForeignKey(MeasurementBook, on_delete=models.CASCADE, related_name='entries')
	boq_item = models.ForeignKey(BOQItem, on_delete=models.PROTECT)
	length = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
	breadth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
	depth = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
	nos = models.DecimalField(max_digits=8, decimal_places=2, default=1)
	measured_quantity = models.DecimalField(max_digits=12, decimal_places=3)
	remarks = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return f"{self.measurement_book.mb_number} - {self.boq_item.item_code}"
