<img width="1127" alt="Screenshot 2023-09-24 at 4 41 20 AM" src="https://github.com/sarthak-kumar-shailendra/store_monitoring/assets/69191344/0ca50d4c-3f96-4715-a18a-27567912dcc6"><img width="1007" alt="Screenshot 2023-09-24 at 4 40 53 AM" src="https://github.com/sarthak-kumar-shailendra/store_monitoring/assets/69191344/9eb8384c-f947-4bec-92d2-6878e16df6c0">Loop monitors several restaurants in the US and needs to monitor if the store is online or not. All restaurants are supposed to be online during their business hours. Due to some unknown reasons, a store might go inactive for a few hours. Restaurant owners want to get a report of the how often this happened in the past.   
## Data sources

We will have 3 sources of data 

1. We poll every store roughly every hour and have data about whether the store was active or not in a CSV.  The CSV has 3 columns (`store_id, timestamp_utc, status`) where status is active or inactive.  All timestamps are in **UTC**
    1. Data can be found in CSV format [here](https://drive.google.com/file/d/1UIx1hVJ7qt_6oQoGZgb8B3P2vd1FD025/view?usp=sharing)
2. We have the business hours of all the stores - schema of this data is `store_id, dayOfWeek(0=Monday, 6=Sunday), start_time_local, end_time_local`
    1. These times are in the **local time zone**
    2. If data is missing for a store, assume it is open 24*7
    3. Data can be found in CSV format [here](https://drive.google.com/file/d/1va1X3ydSh-0Rt1hsy2QSnHRA4w57PcXg/view?usp=sharing)
3. Timezone for the stores - schema is `store_id, timezone_str`
    1. If data is missing for a store, assume it is America/Chicago
    2. This is used so that data sources 1 and 2 can be compared against each other. 
    3. Data can be found in CSV format [here](https://drive.google.com/file/d/101P9quxHoMZMZCVWQ5o-shonk2lgK1-o/view?usp=sharing)
       
## Data output requirement

We want to output a report to the user that has the following schema

`store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)`

# Solution: - 

- Tech used: 
Python Django Rest framework and SQLLITE3 database.

Data Storage and Missing Data Handling

1. First we store all the timezones and store id in the db Store
2. Then we go through all the business hours csv and row by row insert each record in StoreBusinessHours DB
3. We are maintaing a foreign key of stores db in StoreBusinessHours and Before inserting each record we are checking if that particular store already exists in the Store DB
4. if it exist then we are storing that entry in StoreBusinessHours db
5. else we are first creating an entry in the store db with the timezone 'America/Chicago'. This way we are handling the missing data
6. Coming to the third db which is StoresLogs. Here are following the same logic and keeping a foreign key reference of Stores DB and before inserting we are checking if entry for that particular store already exists or not.
7. if it exist then we are directly storing that entry in StoresLogs db
8. else we are first creating an entry in the store db with the timezone 'America/Chicago'. Here the catch is that if that store doesn't exist in store db so there wont be any entry in StoreBusinessHours as well. That means that this store runs for 24/7 hours and that's how we are handling the missing data here. 

    def create_store(apps, schema_editor):
            Store.objects.all().delete()
            StoreBusinessHours.objects.all().delete()
            StoresLogs.objects.all().delete()
            with open('api/csv_files/timezones.csv','r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    print(row)
                    Store.objects.create(
                        store_id=row['store_id'],
                        timezone_str=row['timezone_str'],
                    )


    def create_store_business_hours(apps, schema_editor):
        with open('api/csv_files/Menu_hours.csv') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                print(row)
                store = Store.objects.filter(store_id=row['store_id']).first()
                if store:
                    store_business_hours = StoreBusinessHours.objects.create(
                        store=store,
                        day=row['day'],
                        start_time_local=row['start_time_local'],
                        end_time_local=row['end_time_local'],
                    )
                    #print(store_business_hours)

                else:
                    storeCreated = Store.objects.create(
                        store_id=row['store_id'],
                        timezone_str='America/Chicago',
                    )
                    print(storeCreated)
                    store = Store.objects.filter(store_id=row['store_id']).first()
                    store_business_hours = StoreBusinessHours.objects.create(
                    store=store,
                    day=row['day'],
                    start_time_local=row['start_time_local'],
                    end_time_local=row['end_time_local'],
                    )
                    #print(store_business_hours)



    def create_stores_logs(apps, schema_editor):
        with open('api/csv_files/store_status.csv') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                print(row)
                store = Store.objects.filter(store_id=row['store_id']).first()
                status = Status.ACTIVE if row['status'] == 'active' else Status.INACTIVE
                timestamp = row['timestamp_utc'][:len(row['timestamp_utc'])-4]
                if store:
                    status_log = StoresLogs.objects.create(
                        store=store,
                        status=status,
                        timestamp_utc=timestamp
                    )
           
                else:
                    storeCreated = Store.objects.create(
                        store_id=row['store_id'],
                        timezone_str='America/Chicago',
                    )
                    print("else")
                    print(storeCreated)
                    store = Store.objects.filter(store_id=row['store_id']).first()
                    for i in range(7):
                        store_business_hours = StoreBusinessHours.objects.create(
                            store=store,
                            day=i,
                            start_time_local='00:00:00',
                            end_time_local='23:59:59',
                        )
                        print(i)

                    status_log = StoresLogs.objects.create(
                        store=store,
                        status=status,
                        timestamp_utc=timestamp
                    )
                    #print(status_log)


API endpoints
1. POST -  http://127.0.0.1:8000/trigger_report/
2. GET - http://127.0.0.1:8000/get_report/:reportid


We have created another DB for reports which has 3 columns - report id, report_data(path where file is stored), status

Here I am storing the file locally in output_csv folder, but we can use S3 for storing and keep the S3 url is report_data
Report id is generated using uuid
Status is pending in the beginning and once the csv is generate, it's status is changed to completed

Here's the step-by-step breakdown of the logic for calculating uptime and downtime for the last hour, day and week:

1. Go through all the stores from the Store DB and for each store calculate last_hour, last_day and last_week data.
2. Store all these data in a csv file 
3.  We have hard coded current timestamp as max timestamp of all the observations logs as this is static data, otherwise we can use current timestamp
4.  For last hour calculation we subtract one hour from current timestamp which is in UTC
5.  Then using this subtracted value we filter all the logs in the last one hour in asc order of timestamp
6.  Since it is told that logs are generated roughly every hour. I am assuming we will have only 1 log entry for a store in an hour
7.  So I am selecting the first log and convert it to local time zone from UTC and we check in the StoreBusiness DB if this log for this store and day falls in business hours or not.
8.  if yes, then based on log status we are measuring uptime and downtime
9. Similarly, we are calculating last_day and last_week, only difference is we are iterating for all the filtered logs for the duration(last day/week) and not taking just 1st entry into consideration.


![Uploading Screenshot 2023-09-24 at 4.40.53 AM.png…]()

<img width="1127" alt="Screenshot 2023-09-24 at 4 41 20 AM" src="https://github.com/sarthak-kumar-shailendra/store_monitoring/assets/69191344/c368d98b-be5f-47ef-9a3a-a4decf57a8f0">

<img width="1008" alt="Screenshot 2023-09-24 at 4 42 01 AM" src="https://github.com/sarthak-kumar-shailendra/store_monitoring/assets/69191344/9cd1cd8d-9703-43d1-9c1f-34b061e9eb1d">


 
