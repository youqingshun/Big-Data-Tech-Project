import argparse
import json

import paho.mqtt.client as mqtt

from station import Station, MySQLStationManager, SQLiteStationManager, StationManager


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="BDT 2021 - Data collector")
    arg_parser.add_argument("-s", "--storage", required=False, default="json", type=str, help="Target storage")
    arg_parser.add_argument("-c", "--collection_rate", required=False, default=60, type=int, help="Collection rate (expressed in seconds)")
    arg_parser.add_argument("-Mu", "--mqtt_user", required=True, type=str, help="MQTT username")
    arg_parser.add_argument("-Mp", "--mqtt_password", required=True, type=str, help="MQTT password")
    arg_parser.add_argument("-Mh", "--mqtt_host", required=True, type=str, help="MQTT host")
    arg_parser.add_argument("-MP", "--mqtt_port", required=False, default=1883, type=int, help="MQTT port")

    arg_parser.add_argument("-mh", "--mysql_host", required=False, type=str, help="MySQL host")
    arg_parser.add_argument("-mP", "--mysql_port", required=False, default=3306, type=int, help="MySQL port")
    arg_parser.add_argument("-mu", "--mysql_user", required=False, type=str, help="MySQL user")
    arg_parser.add_argument("-mp", "--mysql_password", required=False, type=str, help="MySQL password")
    arg_parser.add_argument("-md", "--mysql_database", required=False, type=str, help="MySQL database")

    args = arg_parser.parse_args()

    client = mqtt.Client(client_id="station-storer")
    client.username_pw_set(args.mqtt_user, args.mqtt_password)

    station_manager = StationManager()
    if args.storage == "sqlite":
        station_manager = SQLiteStationManager()
    elif args.storage == "mysql":
        if not args.mysql_host or not args.mysql_port or not args.mysql_database or not args.mysql_user or not args.mysql_password:
            print("MySQL storer requires connection details")
            exit(1)
        station_manager = MySQLStationManager(args.mysql_host, args.mysql_port, args.mysql_database, args.mysql_user, args.mysql_password)


    def when_message_received_do_this(client, user_data, msg):
        str_station = msg.payload.decode()
        raw_station = json.loads(str_station)
        station = Station.from_repr(raw_station)
        print(station)
        station_manager.save([station])

    client.on_message = when_message_received_do_this

    client.connect(args.mqtt_host, port=args.mqtt_port)

    client.subscribe("bdt-2021/+/station")

    client.loop_forever()