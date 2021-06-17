from __future__ import absolute_import, annotations

import argparse
import json
import time
from datetime import datetime
from typing import List

import paho.mqtt.client as mqtt
import requests

from station import MySQLStationManager, Station, SQLiteStationManager, MySQLStationManager


def get_stations_for_trento() -> List[Station]:
    stations = get_stations("https://os.smartcommunitylab.it/core.mobility/getparkingsbyagency/COMUNE_DI_TRENTO", "Trento")
    return stations


# def get_stations_for_rovereto() -> List[Station]:
#     stations = get_stations("https://os.smartcommunitylab.it/core.mobility/bikesharing/rovereto", "Rovereto")
#     return stations


def get_stations(url: str, city: str) -> List[Station]:
    """
    Get the list of stations for a particular url

    :param str url: this is the url to query stations from
    :return: the list of stations
    """
    resp = requests.get(url)
    stations = resp.json()

    station_list = [Station.from_repr(raw_data, city=city, dt=datetime.now()) for raw_data in stations]

    return station_list


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="BDT 2021 - Data collector")
    arg_parser.add_argument("-s", "--storage", required=False, default="json", type=str, help="Target storage")
    arg_parser.add_argument("-c", "--collection_rate", required=False, default=30, type=int, help="Collection rate (expressed in seconds)")
    arg_parser.add_argument("-MYh", "--mysql_host", required=False, type=str,  default= '127.0.0.1', help="Mysql host")
    arg_parser.add_argument("-MYP", "--mysql_port", required=False, type=int, default = 3306, help="Mysql port")
    arg_parser.add_argument("-MYdb", "--mysql_database", required=False, type=str, default= "bdt_station", help="Mysql database")
    arg_parser.add_argument("-MYu", "--mysql_user", required=False, type=str, default= "root", help="Mysql username")
    arg_parser.add_argument("-MYpwsd", "--mysql_password", required=False, type=str, default = "123456", help="Mysql password")
  
    
    # arg_parser.add_argument("-Mu", "--mqtt_user", required=True, type=str, help="MQTT username")
    # arg_parser.add_argument("-Mp", "--mqtt_password", required=True, type=str, help="MQTT password")
    # arg_parser.add_argument("-Mh", "--mqtt_host", required=False, type=str,  default=8888, help="MQTT host")
    # arg_parser.add_argument("-MP", "--mqtt_port", required=True, default=1883, type=int, help="MQTT port")
    args = arg_parser.parse_args()

    if args.storage not in ["json", "sqlite", "mysql"]:
        print(f"Un-supported storage [{args.storage}]")
        exit()

    # client = mqtt.Client(client_id="station-collector")
    # client.username_pw_set(args.mqtt_user, args.mqtt_password)

    # client.connect(args.mqtt_host, port=args.mqtt_port)
    station_manager = MySQLStationManager(args.mysql_host, args.mysql_port, args.mysql_database, args.mysql_user, args.mysql_password)
    while True:

        trento_stations = get_stations_for_trento()
        # rovereto_stations = get_stations_for_rovereto()

        stations = trento_stations
        print(len(stations))

        # for station in stations:
        #     client.publish(f"bdt-2021/{station.city}/station", json.dumps(station.to_repr()))
        
        station_manager.save(stations)
        print("data updated!")

        time.sleep(args.collection_rate)
