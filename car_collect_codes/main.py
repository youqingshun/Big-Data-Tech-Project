from __future__ import absolute_import, annotations

import json
import time
from datetime import datetime
from typing import List, Optional

import requests
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import requests
import argparse

import paho.mqtt.client as mqtt

from station import Station, StationManager


# https://dati.trentino.it/dataset/stazioni-bike-sharing-emotion-trentino

# trento: https://os.smartcommunitylab.it/core.mobility/bikesharing/trento
# rovereto: https://os.smartcommunitylab.it/core.mobility/bikesharing/rovereto



def get_stations_for_trento() -> List[Station]:
    stations = get_stations("https://os.smartcommunitylab.it/core.mobility/getparkingsbyagency/COMUNE_DI_TRENTO", "Trento")
    return stations
    


# def get_stations_for_parkingData() -> List[Station]:
#     stations = get_stations("https://os.smartcommunitylab.it/core.mobility/bikesharing/rovereto", "ParkingData")
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


station_manager = StationManager()

url_trento = "https://os.smartcommunitylab.it/core.mobility/bikesharing/trento"
url_rovereto = "https://os.smartcommunitylab.it/core.mobility/bikesharing/rovereto"
while True:


    trento_stations = get_stations_for_trento()
    # rovereto_stations = get_stations_for_rovereto()

    stations = trento_stations 

    print(len(stations))

    station_manager.save(stations)

    print("data updated!")
    time.sleep(30)




"""
if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="BDT 2021 - Data collector")
    arg_parser.add_argument("-s", "--storage", required=False, default="json", type=str, help="Target storage")
    arg_parser.add_argument("-c", "--collection_rate", required=False, default=60, type=int, help="Collection rate (expressed in seconds)")
    arg_parser.add_argument("-Mu", "--mqtt_user", required=True, type=str, help="MQTT username")
    arg_parser.add_argument("-Mp", "--mqtt_password", required=True, type=str, help="MQTT password")
    arg_parser.add_argument("-Mh", "--mqtt_host", required=True, type=str, help="MQTT host")
    arg_parser.add_argument("-MP", "--mqtt_port", required=False, default=1883, type=int, help="MQTT port")
    args = arg_parser.parse_args()

    if args.storage not in ["json", "sqlite", "mysql"]:
        print(f"Un-supported storage [{args.storage}]")
        exit()

    client = mqtt.Client(client_id="station-collector")
    client.username_pw_set(args.mqtt_user, args.mqtt_password)

    client.connect(args.mqtt_host, port=args.mqtt_port)

    while True:

        trento_stations = get_stations_for_trento()
        # rovereto_stations = get_stations_for_rovereto()

        stations = trento_stations 

        print(len(stations))

        for station in stations:
            client.publish(f"bdt-2021/{station.city}/station", json.dumps(station.to_repr()))

        print("data updated!")

        time.sleep(args.collection_rate)
    
"""
