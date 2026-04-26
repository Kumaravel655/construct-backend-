from rest_framework import serializers

from .models import FundAllotment, FundSource, FundTransaction


class FundSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundSource
        fields = '__all__'


class FundAllotmentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    fund_source_name = serializers.CharField(source='fund_source.name', read_only=True)
    pending_release = serializers.ReadOnlyField()

    class Meta:
        model = FundAllotment
        fields = '__all__'


class FundTransactionSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='allotment.project.name', read_only=True)

    class Meta:
        model = FundTransaction
        fields = '__all__'
