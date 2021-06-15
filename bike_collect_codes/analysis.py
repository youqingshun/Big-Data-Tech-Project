import argparse
from datetime import datetime
from typing import List
from station import StationManager, Station, SQLiteStationManager, MySQLStationManager


def average_slots(snapshots: List[Station]) -> float:
    return sum([snapshot.slots for snapshot in snapshots])/len(snapshots) if len(snapshots) > 0 else 0


def average_bikes(snapshots: List[Station]) -> float:
    return sum([snapshot.bikes for snapshot in snapshots])/len(snapshots) if len(snapshots) > 0 else 0


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="BDT 2021 - Data analyser")
    arg_parser.add_argument("-f", "--from_ts", required=True, type=str, help="From timestamp (ISO format)")
    arg_parser.add_argument("-t", "--to_ts", required=True, type=str, help="To timestamp (ISO format)")
    arg_parser.add_argument("-c", "--city", required=False, default=None, type=str, help="The target city")
    arg_parser.add_argument("-si", "--station_id", required=False, default=None, type=str, help="The id of the target station")
    arg_parser.add_argument("-s", "--storage", required=False, default="json", type=str, help="Target storage")
    args = arg_parser.parse_args()


    
    arg_parser.add_argument("-mh", "--mysql_host", required=False, type=str, help="MySQL host")
    arg_parser.add_argument("-mP", "--mysql_port", required=False, default=3306, type=int, help="MySQL port")
    arg_parser.add_argument("-mu", "--mysql_user", required=False, type=str, help="MySQL user")
    arg_parser.add_argument("-mp", "--mysql_password", required=False, type=str, help="MySQL password")
    arg_parser.add_argument("-md", "--mysql_database", required=False, type=str, help="MySQL database")
    

    try:
        from_dt = datetime.fromisoformat(args.from_ts)
    except Exception as e:
        print(f"Value [{args.from_ts}] for from_ts is malformed") ## use print(f"{}"), the {} contains the other type data rather than string
        exit(1)

    try:
        to_dt = datetime.fromisoformat(args.to_ts)
    except Exception as e:
        print(f"Value [{args.to_ts}] for to_ts is malformed")
        exit(1)

    if args.storage not in ["json", "sqlite", "mysql"]:
        print(f"Un-supported storage [{args.storage}]")
        exit()

    station_manager = StationManager()
    if args.storage == "sqlite":
        station_manager = SQLiteStationManager()
    elif args.storage == "mysql":
        if not args.mysql_host or not args.mysql_port or not args.mysql_database or not args.mysql_user or not args.mysql_password:
            print("MySQL storer requires connection details")
            exit(1)
        station_manager = MySQLStationManager(args.mysql_host, args.mysql_port, args.mysql_database, args.mysql_user, args.mysql_password)

    station_snapshots = station_manager.list()

    station_snapshots_in_time_range = [snapshot for snapshot in station_snapshots if snapshot.dt > from_dt and snapshot.dt < to_dt]

    print("Cross-station hour average:")
    print(" - snapshots considered: %s" % len(station_snapshots_in_time_range))
    print(" - slots: %f" % average_slots(station_snapshots_in_time_range))
    print(" - bikes: %f" % average_bikes(station_snapshots_in_time_range))

    if args.city:

        station_snapshots_for_city = [snapshot for snapshot in station_snapshots_in_time_range if snapshot.city == args.city]

        print("Cross-station hour average for the city of Trento:")
        print(" - snapshots considered: %s" % len(station_snapshots_for_city))
        print(" - slots: %f" % average_slots(station_snapshots_for_city))
        print(" - bikes: %f" % average_bikes(station_snapshots_for_city))

    else:
        print("No filter specified for city: skipping city cross-station hour average computation")

    if args.station_id:

        snapshots_for_station = [snapshot for snapshot in station_snapshots_in_time_range if snapshot.id == args.station_id]

        print("Cross-station hour average the station Aeroporto - Trento in Trento:")
        print(" - snapshots considered: %s" % len(snapshots_for_station))
        print(" - slots: %f" % average_slots(snapshots_for_station))
        print(" - bikes: %f" % average_bikes(snapshots_for_station))

    else:
        print("No filter specified for station: skipping station cross-station hour average computation")
