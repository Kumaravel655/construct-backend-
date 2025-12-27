
from django.contrib import admin
from .models import User, Project, Attendance,Task,Document,Vendor,PurchaseOrder,Budget,Invoice,Communication,SafetyIncident,Equipment,MaterialRequest,QualityInspection


# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Attendance)
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
