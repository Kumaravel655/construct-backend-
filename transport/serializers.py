from rest_framework import serializers

from .models import FuelLog, TripSheet, Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    current_project_name = serializers.CharField(source='current_project.name', read_only=True)
    assigned_driver_name = serializers.CharField(source='assigned_driver.username', read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'


class TripSheetSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(source='vehicle.vehicle_id', read_only=True)
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    distance_km = serializers.ReadOnlyField()

    class Meta:
        model = TripSheet
        fields = '__all__'


class FuelLogSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(source='vehicle.vehicle_id', read_only=True)
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = FuelLog
        fields = '__all__'
