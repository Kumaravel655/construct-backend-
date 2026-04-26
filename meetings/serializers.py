from rest_framework import serializers

from .models import ActionItem, Meeting, MeetingAttendee


class MeetingSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingAttendeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MeetingAttendee
        fields = '__all__'


class ActionItemSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = ActionItem
        fields = '__all__'
