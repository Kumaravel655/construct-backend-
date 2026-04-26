from django.conf import settings
from django.db import models


class Drawing(models.Model):
	DRAWING_TYPES = [
		('plan', 'Plan Drawing'),
		('section', 'Section Drawing'),
		('elevation', 'Elevation'),
		('as_built', 'As-Built Drawing'),
		('structural', 'Structural Drawing'),
		('electrical', 'Electrical Drawing'),
		('plumbing', 'Plumbing Drawing'),
		('landscape', 'Landscape Drawing'),
	]

	STATUS_CHOICES = [
		('draft', 'Draft'),
		('under_review', 'Under Review'),
		('approved', 'Approved'),
		('superseded', 'Superseded'),
		('as_built', 'As-Built'),
	]

	drawing_number = models.CharField(max_length=100)
	project = models.ForeignKey('core.Project', on_delete=models.CASCADE)
	task = models.ForeignKey('core.Task', on_delete=models.SET_NULL, null=True, blank=True)
	drawing_type = models.CharField(max_length=20, choices=DRAWING_TYPES)
	title = models.CharField(max_length=200)
	scale = models.CharField(max_length=50, blank=True)
	revision = models.CharField(max_length=10, default='A')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
	file = models.FileField(upload_to='drawings/')
	thumbnail = models.ImageField(upload_to='drawing_thumbs/', blank=True)
	drawn_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='drawn')
	checked_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='checked_drawings',
	)
	approved_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='approved_drawings',
	)
	drawing_date = models.DateField()
	approval_date = models.DateField(null=True, blank=True)
	notes = models.TextField(blank=True)
	superseded_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ['drawing_number', 'revision']

	def __str__(self):
		return f"{self.drawing_number}-{self.revision}"
