from django.conf import settings
from django.db import models


class RateAnalysis(models.Model):
	item_code = models.CharField(max_length=50, unique=True)
	description = models.TextField()
	unit = models.CharField(max_length=20)
	materials_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	labour_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	machinery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	overhead_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10)
	profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10)
	reference_schedule = models.CharField(max_length=100, blank=True)
	valid_from = models.DateField()
	valid_to = models.DateField(null=True, blank=True)
	prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

	@property
	def base_rate(self):
		return self.materials_cost + self.labour_cost + self.machinery_cost

	@property
	def total_rate(self):
		base = self.base_rate
		overhead = base * (self.overhead_percentage / 100)
		profit = (base + overhead) * (self.profit_percentage / 100)
		return base + overhead + profit

	def __str__(self):
		return self.item_code


class TenderEstimate(models.Model):
	tender = models.ForeignKey('government_relations.TenderApplication', on_delete=models.CASCADE)
	project_name = models.CharField(max_length=200)
	location = models.CharField(max_length=200)
	total_estimated_cost = models.DecimalField(max_digits=15, decimal_places=2)
	contingency_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
	gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18)
	prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	prepared_date = models.DateField()

	def __str__(self):
		return f"Tender Estimate {self.id}"


class ComparativeStatement(models.Model):
	tender = models.ForeignKey('government_relations.TenderApplication', on_delete=models.CASCADE)
	prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	comparison_date = models.DateField()
	lowest_bidder = models.CharField(max_length=200, blank=True)
	recommendation = models.TextField(blank=True)
	attachment = models.FileField(upload_to='comparative_statements/', blank=True)

	def __str__(self):
		return f"Comparative Statement {self.id}"
