from django.conf import settings
from django.db import models


class GovernmentDepartment(models.Model):
	DEPARTMENT_TYPE_CHOICES = [
		('pwd', 'PWD'),
		('drda', 'DRDA'),
		('highways', 'Highways'),
		('municipality', 'Municipality'),
		('other', 'Other'),
	]

	name = models.CharField(max_length=200)
	department_type = models.CharField(max_length=30, choices=DEPARTMENT_TYPE_CHOICES, default='other')
	contact_officer = models.CharField(max_length=200)
	contact_phone = models.CharField(max_length=20)
	contact_email = models.EmailField(blank=True)
	district = models.CharField(max_length=100)
	notes = models.TextField(blank=True)

	def __str__(self):
		return self.name


class TenderApplication(models.Model):
	STATUS_CHOICES = [
		('draft', 'Draft'),
		('submitted', 'Submitted'),
		('under_review', 'Under Review'),
		('approved', 'Approved'),
		('rejected', 'Rejected'),
		('withdrawn', 'Withdrawn'),
	]

	tender_number = models.CharField(max_length=100, unique=True)
	department = models.ForeignKey(GovernmentDepartment, on_delete=models.PROTECT)
	project = models.ForeignKey('core.Project', on_delete=models.SET_NULL, null=True, blank=True)
	tender_value = models.DecimalField(max_digits=15, decimal_places=2)
	submission_date = models.DateField()
	decision_date = models.DateField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
	documents = models.FileField(upload_to='tenders/', blank=True)
	notes = models.TextField(blank=True)
	submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.tender_number


class GovernmentContact(models.Model):
	department = models.ForeignKey(GovernmentDepartment, on_delete=models.CASCADE)
	officer_name = models.CharField(max_length=200)
	designation = models.CharField(max_length=100)
	phone = models.CharField(max_length=20)
	email = models.EmailField(blank=True)
	relationship_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
	last_meeting_date = models.DateField(null=True, blank=True)
	notes = models.TextField(blank=True)

	def __str__(self):
		return f"{self.officer_name} ({self.department.name})"
