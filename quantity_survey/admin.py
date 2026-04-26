from django.contrib import admin

from .models import BOQ, BOQItem, MeasurementBook, MeasurementEntry

admin.site.register(BOQ)
admin.site.register(BOQItem)
admin.site.register(MeasurementBook)
admin.site.register(MeasurementEntry)
