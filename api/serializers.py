from rest_framework import serializers

from api.models import Report, ReportStatus 

class ReportSerializer(serializers.ModelSerializer):
     class Meta:
        model = Report
        fields = "__all__"