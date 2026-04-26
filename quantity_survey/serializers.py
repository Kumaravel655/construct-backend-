from rest_framework import serializers

from .models import BOQ, BOQItem, MeasurementBook, MeasurementEntry


class BOQSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = BOQ
        fields = '__all__'


class BOQItemSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField()

    class Meta:
        model = BOQItem
        fields = '__all__'


class MeasurementBookSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = MeasurementBook
        fields = '__all__'


class MeasurementEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementEntry
        fields = '__all__'
