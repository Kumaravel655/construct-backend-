from rest_framework import serializers

from .models import ComparativeStatement, RateAnalysis, TenderEstimate


class RateAnalysisSerializer(serializers.ModelSerializer):
    base_rate = serializers.ReadOnlyField()
    total_rate = serializers.ReadOnlyField()

    class Meta:
        model = RateAnalysis
        fields = '__all__'


class TenderEstimateSerializer(serializers.ModelSerializer):
    tender_number = serializers.CharField(source='tender.tender_number', read_only=True)

    class Meta:
        model = TenderEstimate
        fields = '__all__'


class ComparativeStatementSerializer(serializers.ModelSerializer):
    tender_number = serializers.CharField(source='tender.tender_number', read_only=True)

    class Meta:
        model = ComparativeStatement
        fields = '__all__'
