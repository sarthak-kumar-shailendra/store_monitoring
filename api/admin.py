from django.contrib import admin
from .models import Store, StoresLogs, StoreBusinessHours, Report

# Register your models here.
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'timezone_str')
    list_filter = ('timezone_str',)
    search_fields = ('store_id',)

@admin.register(StoreBusinessHours)
class StoreBusinessHours(admin.ModelAdmin):
    list_display = ('store', 'day', 'start_time_local', 'end_time_local')
    raw_id_fields = ('store',)
    list_filter = ('day',)
    search_fields = ('store_id',)

@admin.register(StoresLogs)
class StoresLogsAdmin(admin.ModelAdmin):
    list_display = ('store', 'status', 'timestamp_utc')
    raw_id_fields = ('store',)
    list_filter = ('status',)
    search_fields = ('store_id',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'status', 'report_data')
    list_filter = ('status',)
    search_fields = ('report_id',)