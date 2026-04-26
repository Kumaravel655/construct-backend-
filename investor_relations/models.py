from django.conf import settings
from django.db import models


class Investor(models.Model):
	name = models.CharField(max_length=200)
	company = models.CharField(max_length=200, blank=True)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	investment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
	investment_date = models.DateField(null=True, blank=True)
	equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.name


class InvestorReport(models.Model):
	REPORT_TYPES = [
		('profit_loss', 'Profit & Loss'),
		('progress_update', 'Project Progress'),
		('financial_summary', 'Financial Summary'),
		('future_investment', 'Future Investment Plan'),
	]

	investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='reports')
	report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
	title = models.CharField(max_length=200)
	period_from = models.DateField()
	period_to = models.DateField()
	content = models.TextField()
	attachment = models.FileField(upload_to='investor_reports/', blank=True)
	sent_date = models.DateField(null=True, blank=True)
	is_sent = models.BooleanField(default=False)
	prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title
