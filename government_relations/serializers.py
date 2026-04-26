from rest_framework import serializers

from .models import GovernmentContact, GovernmentDepartment, TenderApplication


class GovernmentDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentDepartment
        fields = '__all__'


class TenderApplicationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TenderApplication
        fields = '__all__'


class GovernmentContactSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = GovernmentContact
        fields = '__all__'
