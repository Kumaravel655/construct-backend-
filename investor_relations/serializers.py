from rest_framework import serializers

from .models import Investor, InvestorReport


class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'


class InvestorReportSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.name', read_only=True)

    class Meta:
        model = InvestorReport
        fields = '__all__'
