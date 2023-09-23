from django.db import models

class Store(models.Model):
    store_id = models.BigIntegerField(unique=True)
    timezone_str = models.CharField(max_length=255)

    def __str__(self):
        return str(self.store_id)

class Day(models.IntegerChoices):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class StoreBusinessHours(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='business_hours')
    day = models.IntegerField(choices=Day.choices)
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()
    

class Status(models.IntegerChoices):
    INACTIVE = 0
    ACTIVE = 1

class StoresLogs(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='logs')
    timestamp_utc = models.DateTimeField()
    status = models.IntegerField(choices=Status.choices)
    
  
class ReportStatus(models.IntegerChoices):
    PENDING = 0
    COMPLETED = 1

class Report(models.Model):
    report_id = models.CharField(primary_key=True, editable=False,max_length=255)
    status = models.IntegerField(choices=ReportStatus.choices)
    report_data = models.CharField(max_length=255, null=True)
