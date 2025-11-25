from django.contrib import admin
from .models import User, Project, Attendance,Task,Document,Vendor,PurchaseOrder,Budget,Invoice


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
