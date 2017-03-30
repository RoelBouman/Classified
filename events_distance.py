import numpy as np
import pandas as pd
import datetime as dt
import os
import sys

from haversine import haversine

CSV_PATH_PREFIX = 'MLiP/'
CSV_SRC_PREFIX = '../unzipped/'

pd.set_option('display.width', None)

events = pd.read_csv(CSV_SRC_PREFIX + 'events.csv', parse_dates=['timestamp'], infer_datetime_format=True)

distance_events = pd.DataFrame(columns=["device_id", "date", "day_distance"])

events.sort_values(['device_id', 'timestamp'], ascending=[True, True], inplace=True)

per_device = events.groupby('device_id')

for device, device_events in per_device:
    per_day = device_events.groupby(device_events['timestamp'].dt.date)
    #print "{}".format(device)
    num_days = 0
    days_distance = []
    for date, date_events in per_day:
        prev_lat = None
        prev_long = None
        total_distance = 0.0
        for ev in date_events.itertuples():
            if ev.latitude == 0.0 or ev.longitude == 0.0:
                continue
            if prev_lat == None and prev_long == None:
                prev_lat  = float(ev.latitude)
                prev_long = float(ev.longitude)
                continue
            if prev_lat == ev.latitude and prev_long == ev.longitude:
                continue
            total_distance += haversine((prev_lat, prev_long), (float(ev.latitude), float(ev.longitude)))
            prev_lat  = float(ev.latitude)
            prev_long = float(ev.longitude)
        #print "  {}: {}".format(date, total_distance)
        days_distance.append(total_distance)
        distance_events = distance_events.append({"device_id": str(device), "date": date, "day_distance": total_distance}, ignore_index=True)

    #mean_dist = round(np.mean(days_distance), 2)
    #std_dist  = round(np.std(days_distance), 2)

if not os.path.isfile(CSV_PATH_PREFIX + 'device_distance.csv'):
    events.to_csv(CSV_PATH_PREFIX + 'device_distance.csv', index=False)

if not os.path.isfile(CSV_PATH_PREFIX + 'device_day_distance.csv'):
    distance_events.to_csv(CSV_PATH_PREFIX + 'device_day_distance.csv', index=False)