from rest_framework import serializers

from .models import Drawing


class DrawingSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = Drawing
        fields = '__all__'
