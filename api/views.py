import os
from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.helper import generateReport

from api.serializers import ReportSerializer
from store_monitoring import settings
from .models import Report, ReportStatus
import uuid


class ReportViewSet(ModelViewSet):
    queryset = Report.objects.all();
   
    def retrieve(self, request, pk, *args, **kwargs):
        try:      
            report_status =  Report.objects.get(report_id=pk)
            data = ReportSerializer(report_status).data
            
            if report_status.status == ReportStatus.PENDING:
                data['status'] = "PENDING"
                return Response(data, status=status.HTTP_200_OK)
           
            if os.path.exists(data['report_data']):
                with open(data['report_data'], 'r') as fh:
                    response = Response(fh.read(), content_type="text/csv")
                    response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(data['report_data'])
                    return response
            
            return Response(data, status=status.HTTP_200_OK)

            
        except Report.DoesNotExist:
                return Response({'error': 'No such data found. Please recheck REPORT_ID'},
                                status=status.HTTP_404_NOT_FOUND)
            
       
    def create(self, request, *args, **kwargs):
        try:
            report_id = str(uuid.uuid4())
            Report.objects.create(report_id=report_id, status=ReportStatus.PENDING)
            
            data = generateReport(report_id)

            report_obj = Report.objects.get(report_id=report_id)
            report_obj.report_data= settings.OUTPUT_CSV_FILES_ROOT + "/" + report_id + ".csv"
            report_obj.status=ReportStatus.COMPLETED
            report_obj.save()
                
            return Response({"report_id": report_id}, status=status.HTTP_201_CREATED)
        except:
            return Response({'error': "INTERNAL SERVER ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

