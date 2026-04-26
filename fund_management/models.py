from django.conf import settings
from django.db import models


class FundSource(models.Model):
	SOURCE_TYPES = [
		('bank_loan', 'Bank Loan'),
		('working_capital', 'Working Capital'),
		('equipment_finance', 'Equipment Finance'),
		('nbfc', 'NBFC'),
		('partner', 'Partner Funding'),
		('own_funds', 'Own Funds'),
	]

	name = models.CharField(max_length=200)
	source_type = models.CharField(max_length=30, choices=SOURCE_TYPES)
	institution_name = models.CharField(max_length=200)
	sanctioned_amount = models.DecimalField(max_digits=15, decimal_places=2)
	interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	disbursed_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
	repaid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)
	account_number = models.CharField(max_length=100, blank=True)
	is_active = models.BooleanField(default=True)
	notes = models.TextField(blank=True)

	def __str__(self):
		return self.name


class FundAllotment(models.Model):
	project = models.ForeignKey('core.Project', on_delete=models.CASCADE, related_name='fund_allotments')
	fund_source = models.ForeignKey(FundSource, on_delete=models.PROTECT)
	allotment_type = models.CharField(max_length=50)
	allotted_amount = models.DecimalField(max_digits=15, decimal_places=2)
	released_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
	allotment_date = models.DateField()
	release_date = models.DateField(null=True, blank=True)
	approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	notes = models.TextField(blank=True)

	@property
	def pending_release(self):
		return self.allotted_amount - self.released_amount

	def __str__(self):
		return f"{self.project.name} - {self.allotment_type}"


class FundTransaction(models.Model):
	TRANSACTION_TYPES = [
		('disbursement', 'Disbursement'),
		('repayment', 'Repayment'),
		('advance', 'Site Advance'),
		('release', 'Fund Release'),
	]

	allotment = models.ForeignKey(FundAllotment, on_delete=models.CASCADE, related_name='transactions')
	transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
	amount = models.DecimalField(max_digits=15, decimal_places=2)
	transaction_date = models.DateField()
	reference_number = models.CharField(max_length=100, blank=True)
	processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	notes = models.TextField(blank=True)

	def __str__(self):
		return f"{self.allotment.id} - {self.transaction_type}"
