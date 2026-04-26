from django.contrib import admin

from .models import GovernmentContact, GovernmentDepartment, TenderApplication

admin.site.register(GovernmentDepartment)
admin.site.register(TenderApplication)
admin.site.register(GovernmentContact)
