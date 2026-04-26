from django.contrib import admin

from .models import ActionItem, Meeting, MeetingAttendee

admin.site.register(Meeting)
admin.site.register(MeetingAttendee)
admin.site.register(ActionItem)
