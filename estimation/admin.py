from django.contrib import admin

from .models import ComparativeStatement, RateAnalysis, TenderEstimate

admin.site.register(RateAnalysis)
admin.site.register(TenderEstimate)
admin.site.register(ComparativeStatement)
