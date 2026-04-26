from django.contrib import admin

from .models import FuelLog, TripSheet, Vehicle

admin.site.register(Vehicle)
admin.site.register(TripSheet)
admin.site.register(FuelLog)
