from datetime import datetime
from typing import List
from station import Station, StationManager

def average_slots(snapshots: List[Station]) -> float:
    return sum([snapshot.slots for snapshot in snapshots])/len(snapshots)

def average_bikes(snapshots: List[Station]) -> float:
    return sum([snapshot.bikes for snapshot in snapshots])/len(snapshots)

station_manager = StationManager()
station_snapshots = station_manager.list()

# Selecting stations for a given time range: 2021-05-20 09:00:00 - 2021-05-20 10:00:00
station_snapshots_in_time_range = [snapshot for snapshot in station_snapshots if snapshot.dt > datetime(2021, 5, 20, 9, 0, 0) and snapshot.dt < datetime(2021, 5, 20, 10, 0, 0)]

print("Cross station hour average:")
print(" -slots: %f" % average_slots(station_snapshots_in_time_range))
print(" -bikes: %f" % average_bikes(station_snapshots_in_time_range))

station_snapshots_for_city = [snapshot for snapshot in station_snapshots_in_time_range if snapshot.city == "Trento"]

print("Cross station hour average for the city of Trento:")
print(" -slots: %f" % average_slots(station_snapshots_for_city))
print(" -bikes: %f" % average_bikes(station_snapshots_for_city))

snapshots_for_station = [snapshot for snapshot in station_snapshots_for_city if snapshot.id == "10.14 Aeroporto - Trento"]

print("Cross station hour average the station Aeroporto - Trento in Trento:")
print(" -slots: %f" % average_slots(snapshots_for_station))
print(" -bikes: %f" % average_bikes(snapshots_for_station))