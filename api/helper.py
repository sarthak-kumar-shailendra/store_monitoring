from store_monitoring import settings
from .models import Status, Store, StoreBusinessHours, StoresLogs, Report
from django.utils import timezone 
from pytz import timezone as pytz_timezone
import datetime
from datetime import datetime as dt
import csv
import os

def generateReport(report_id):
    csv_data = []
    stores = Store.objects.all()
    for store in stores:
        data = generate_report_store(store)
        csv_data.append(data)
    generate_csv_file(report_id, csv_data)
    


def generate_report_store(store):
    last_utc_timestamp = StoresLogs.objects.all().order_by('-timestamp_utc').first().timestamp_utc

    last_hour = last_hour_data(store, last_utc_timestamp)
    last_day = last_day_data(store, last_utc_timestamp)
    last_week = last_week_data(store, last_utc_timestamp)

    data = []
    data.append(store.store_id)
    data.extend(list(last_hour.values()))
    data.extend(list(last_day.values()))
    data.extend(list(last_week.values()))
    return data


def last_hour_data(store, last_utc_timestamp):
    #if no logs found or current time not in business hours
    last_hour_data = {"uptime" : 0 , "downtime" : 0 }

    prev_hour = last_utc_timestamp - datetime.timedelta(hours=1)
    
    last_hour_logs = store.logs.filter(timestamp_utc__gte=prev_hour).order_by('timestamp_utc')
    # since it is given that logs are generated roughly every hour
    # so we can assume that if we find a log status in the given hour
    # to be active then the store is active for entire hour
 
    if last_hour_logs:
        log = last_hour_logs[0]
            
        target_timezone = pytz_timezone(store.timezone_str)
        local_time = log.timestamp_utc.astimezone(target_timezone)
        log_current_day = local_time.weekday()
        log_current_time = local_time.time()

        # checking if current time lies in between business hours
        is_between_business_hours = store.business_hours.filter(day=log_current_day,start_time_local__lte=log_current_time,end_time_local__gte=log_current_time).exists()
        if not is_between_business_hours:
            return last_hour_data

        if log.status == Status.ACTIVE:
            last_hour_data["uptime"] += 60
        else:
            last_hour_data["downtime"] += 60

    return last_hour_data
    

def last_day_data(store, last_utc_timestamp):
     #if no logs found or current time not in business hours
    last_day_data = {"uptime" : 0 , "downtime" : 0}

    prev_day = last_utc_timestamp - datetime.timedelta(days=1)
    
    # getting all the logs in last one day
    last_day_logs = store.logs.filter(timestamp_utc__gte=prev_day).order_by('timestamp_utc')
    for log in last_day_logs:
        target_timezone = pytz_timezone(store.timezone_str)
        local_time = log.timestamp_utc.astimezone(target_timezone)
        log_current_day = local_time.weekday()
        log_current_time = local_time.time()

        # checkig if log is in store business hours
        log_in_store_business_hours = store.business_hours.filter(
            day=log_current_day,
            start_time_local__lte=log_current_time,
            end_time_local__gte=log_current_time
            ).exists()
        
        if not log_in_store_business_hours:
            continue

        if log.status == Status.ACTIVE:
            last_day_data["uptime"] += 1
        else:
            last_day_data["downtime"] += 1

    return last_day_data

def last_week_data(store, last_utc_timestamp):
    last_week_data = {"uptime" : 0 , "downtime" : 0}

    prev_week = last_utc_timestamp - datetime.timedelta(days=7)
    
    # getting all the logs in last one week
    last_week_logs = store.logs.filter(timestamp_utc__gte=prev_week).order_by('timestamp_utc')
    for log in last_week_logs:

        target_timezone = pytz_timezone(store.timezone_str)
        local_time = log.timestamp_utc.astimezone(target_timezone)
        log_current_day = local_time.weekday()
        log_current_time = local_time.time()

         # checkig if log is in store business hours
        log_in_store_business_hours = store.business_hours.filter(
            day=log_current_day,
            start_time_local__lte=log_current_time,
            end_time_local__gte=log_current_time
            ).exists()
        
        if not log_in_store_business_hours:
            continue
        if log.status == Status.ACTIVE:
            last_week_data["uptime"] += 1
        else:
            last_week_data["downtime"] += 1
    
    return last_week_data

def generate_csv_file(report_id, csv_data):
        file_name = f"{report_id}.csv"
        temp_file_path = os.path.join(settings.OUTPUT_CSV_FILES_ROOT,file_name)
        with open(temp_file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["store_id", "uptime_last_hour(in minutes)", "uptime_last_day(in hours)", "update_last_week(in hours)", "downtime_last_hour(in minutes)", "downtime_last_day(in hours)", "downtime_last_week(in hours)"])
            for data in csv_data:
                csv_writer.writerow(data)
