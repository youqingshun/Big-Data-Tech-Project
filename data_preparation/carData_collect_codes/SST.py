from __future__ import absolute_import, annotations, barry_as_FLUFL
import sqlite3
import json
from datetime import datetime
from typing import Optional, List
import os
import mysql.connector



class Position:

    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon



class Station:

    def __init__(self, description: str, name: str,  slotsTotal: int, slotsAvailable: int, monitored: str, extra:str, city: str, position: Position, dt: datetime):
        self.description = description
        self.name = name
        self.slotsTotal = slotsTotal
        self.slotsAvailable = slotsAvailable
        self.position = position
        self.monitored = monitored
        self.extra = extra
        self.city = city
        self.dt = dt
# {'name': '10.02 Top Center', 'address': 'Via Pranzelores / Via Giuseppe Gilli', 'id': '10.02 Top Center - Trento', 'bikes': 7, 'slots': 17, 'totalSlots': 24, 'position': [46.09010372321067, 11.118583717279193]}

    
    def to_repr(self) -> dict:  ## make class Station to json format
              return {
            "name": self.name,
            "description": self.description,
            "slotsTotal": self.slotsTotal,
            "slotsAvailable": self.slotsAvailable,
            "extra":{"parkAndRide":self.extra},
            "monitored": self.monitored,
            "city": self.city,
            "position": [
                self.position.lat, self.position.lon
            ],
            "timestamp": self.dt.isoformat()
        }

    @staticmethod
    def from_repr(raw_data: dict, city: Optional[str] = None, dt: Optional[datetime] = None) -> Station:

        if not city and "city" not in raw_data:
            raise Exception("Can not build Station model: city information missing")

        if not dt and "timestamp" not in raw_data:
            raise Exception("Can not build Station model: timestamp information is missing")

        return Station(
            raw_data["description"],
            raw_data["name"],
            raw_data["slotsTotal"],
            raw_data["slotsAvailable"],
            raw_data["monitored"],
            raw_data["extra"]["parkAndRide"],
            raw_data["city"] if "city" in raw_data else city,
            
            Position(
                raw_data["position"][0],
                raw_data["position"][1]
            ),
            datetime.fromisoformat(raw_data["timestamp"]) if "timestamp" in raw_data else dt
        )

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)


class StationManager:

    STATION_FILE = "D:/courses and slides/data/parking 0519-0522.json"

    def __init__(self) -> None:
        if not os.path.isfile(self.STATION_FILE):
            with open("D:/courses and slides/data/parking 0519-0522.json", "w") as f:
                json.dump([], f)

    def save(self, stations: List[Station]) -> None:

        old_stations = self.list()
        update_stations = old_stations + stations

        with open("D:/courses and slides/data/parking 0519-0522.json", "w") as f:
            json.dump(
                [station.to_repr() for station in update_stations],
                f,
                indent=4
            )

    def list(self) -> List[Station]:
        with open("D:/courses and slides/data/parking 0519-0522.json", "r") as f:
            raw_stations = json.load(f)
            return [Station.from_repr(raw_station) for raw_station in raw_stations]


class SQLiteStationManager:

    DB_NAME = "station_parking.db"

    def save(self, stations: List[Station]) -> None:
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        query = "INSERT into station0 (description, name, slotsTotal, slotsAvailable, monitored, parkAndRide, city,  lat, lon, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        for station in stations:
            cursor.execute(query, (station.description, station.name, station.slotsTotal, station.slotsAvailable, station.monitored, station.extra, station.city, station.position.lat, station.position.lon, station.dt.isoformat()))
            conn.commit()

        conn.close()

   
    def list(self) -> List[Station]:
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        query = "SELECT description, name, slotsTotal, slotsAvailable, monitored, parkAndRide, city, lat, lon, timestamp from station0"
        cursor.execute(query)
        rows = cursor.fetchall()

        stations = []
        for description, name, slotsTotal, slotsAvailable, monitored, parkAndRide, city, lat, lon, timestamp in rows:
            stations.append(
                Station(
                    description,
                    name,
                    slotsTotal, slotsAvailable, monitored,
                    parkAndRide,
                    city,
                    Position(lat, lon),
                    datetime.fromisoformat(timestamp)
                )
            )

        conn.close()
        return stations
       

class MySQLStationManager:

    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        self.connection.autocommit = True

    def save(self, stations: List[Station]) -> None:
        cursor = self.connection.cursor()
        query = "INSERT into 0519_0522parking (description, name, slotsTotal, slotsAvailable, monitored, parkAndRide, city, lat, lon, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for station in stations:
            cursor.execute(query, (
                station.description,
                station.name,
                station.slotsTotal,
                station.slotsAvailable,
                station.monitored,
                station.extra,
                station.city,
                station.position.lat,
                station.position.lon,
                station.dt.isoformat()
            ))

        cursor.close()

    def list(self) -> List[Station]:
        cursor = self.connection.cursor()
        query = "SELECT description, name, slotsTotal, slotsAvailable, monitored, parkAndRide, city, lat, lon, timestamp from station"
        cursor.execute(query)

        stations = []
        for description, name, slotsTotal, slotsAvailable, monitored, parkAndRide, city, lat, lon, timestamp in cursor:
            stations.append(Station(
                description,
                name,
                slotsTotal, slotsAvailable, monitored, parkAndRide, city,
                Position(lat, lon),
                datetime.fromisoformat(timestamp)
            ))

        cursor.close()

        return stations   
