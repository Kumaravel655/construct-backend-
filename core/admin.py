
from django.contrib import admin
from .models import (
	Attendance,
	AttendanceSession,
	Budget,
	Communication,
	DailyWorkItem,
	Document,
	Equipment,
	Invoice,
	MaterialRequest,
	Project,
	PurchaseOrder,
	QualityInspection,
	SafetyIncident,
	Task,
	User,
	Vendor,
)


# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Attendance)
admin.site.register(AttendanceSession)
admin.site.register(DailyWorkItem)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(Budget)
admin.site.register(Invoice)
admin.site.register(Communication)
admin.site.register(SafetyIncident)
admin.site.register(Equipment)
admin.site.register(MaterialRequest)
admin.site.register(QualityInspection)
