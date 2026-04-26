from django.conf import settings
from django.db import models


class Meeting(models.Model):
	MEETING_TYPES = [
		('daily', 'Daily Site Work Review'),
		('weekly', 'Weekly Project Progress Review'),
		('monthly', 'Monthly MD Review'),
	]

	STATUS_CHOICES = [
		('scheduled', 'Scheduled'),
		('in_progress', 'In Progress'),
		('completed', 'Completed'),
		('cancelled', 'Cancelled'),
	]

	meeting_id = models.CharField(max_length=50, unique=True)
	meeting_type = models.CharField(max_length=20, choices=MEETING_TYPES)
	project = models.ForeignKey('core.Project', on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=200)
	scheduled_date = models.DateField()
	scheduled_time = models.TimeField()
	actual_date = models.DateField(null=True, blank=True)
	location = models.CharField(max_length=200)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
	agenda = models.TextField()
	minutes = models.TextField(blank=True)
	organized_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		related_name='organized_meetings',
	)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.meeting_id


class MeetingAttendee(models.Model):
	meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendees')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	is_present = models.BooleanField(default=False)
	remarks = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return f"{self.meeting.meeting_id} - {self.user.username}"


class ActionItem(models.Model):
	PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
	STATUS_CHOICES = [('open', 'Open'), ('in_progress', 'In Progress'), ('done', 'Done'), ('overdue', 'Overdue')]

	meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
	description = models.TextField()
	assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	due_date = models.DateField()
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
	completion_date = models.DateField(null=True, blank=True)
	remarks = models.TextField(blank=True)

	def __str__(self):
		return f"Action {self.id}"
