from django.contrib import admin

from .models import FundAllotment, FundSource, FundTransaction

admin.site.register(FundSource)
admin.site.register(FundAllotment)
admin.site.register(FundTransaction)
