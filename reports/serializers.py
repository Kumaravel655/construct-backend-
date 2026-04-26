from rest_framework import serializers

from .models import DailyWorkReport


class DailyWorkReportSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)

    class Meta:
        model = DailyWorkReport
        fields = '__all__'
