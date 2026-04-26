from django.conf import settings
from django.db import models


class DailyWorkReport(models.Model):
	STATUS_CHOICES = [
		('draft', 'Draft'),
		('submitted', 'Submitted to PM'),
		('pm_reviewed', 'PM Reviewed'),
		('om_consolidated', 'OM Consolidated'),
		('md_reviewed', 'MD Reviewed'),
	]

	report_id = models.CharField(max_length=50, unique=True)
	project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
	report_date = models.DateField()
	submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='daily_reports')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

	work_completed_today = models.TextField()
	work_planned_tomorrow = models.TextField()
	issues_faced = models.TextField(blank=True)

	total_workers_present = models.IntegerField(default=0)
	total_workers_absent = models.IntegerField(default=0)
	subcontractor_workers = models.IntegerField(default=0)

	materials_used = models.JSONField(default=list)
	equipment_used = models.JSONField(default=list)

	weather_condition = models.CharField(max_length=50, blank=True)
	rainfall_mm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
	overall_progress_percentage = models.DecimalField(max_digits=5, decimal_places=2)

	pm_remarks = models.TextField(blank=True)
	pm_reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='pm_reviewed_reports',
	)
	pm_reviewed_at = models.DateTimeField(null=True, blank=True)

	om_remarks = models.TextField(blank=True)
	om_reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='om_reviewed_reports',
	)
	om_reviewed_at = models.DateTimeField(null=True, blank=True)

	md_remarks = models.TextField(blank=True)
	md_reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='md_reviewed_reports',
	)
	md_reviewed_at = models.DateTimeField(null=True, blank=True)

	photo_attachments = models.ManyToManyField('core.Document', blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.report_id
