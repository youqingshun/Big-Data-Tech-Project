from __future__ import absolute_import, annotations

import json
import os
import sqlite3
import mysql.connector
from datetime import datetime
from typing import Optional, List


class Position:

    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon


class Station:

    def __init__(self, station_id: str, name: str, address: str, bikes: int, slots: int, city: str, position: Position, dt: datetime):
        self.id = station_id
        self.name = name
        self.address = address
        self.bikes = bikes
        self.slots = slots
        self.city = city
        self.position = position
        self.dt = dt

    def to_repr(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "address": self.address,
            "bikes": self.bikes,
            "slots": self.slots,
            "totalSlots": self.bikes + self.slots,
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
            raw_data["id"],
            raw_data["name"],
            raw_data["address"],
            raw_data["slots"],
            raw_data["bikes"],
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

    STATION_FILE = "D:/courses and slides/bdt-2021-master/src/stations.json"

    def __init__(self) -> None:
        if not os.path.isfile(self.STATION_FILE):
            with open("D:/courses and slides/bdt-2021-master/src/stations.json", "w") as f:
                json.dump([], f)

    def save(self, stations: List[Station]) -> None:
        old_stations = self.list()
        update_stations = old_stations + stations

        with open("D:/courses and slides/bdt-2021-master/src/stations.json", "w") as f:
            json.dump(
                [station.to_repr() for station in update_stations],
                f,
                indent=4
            )

    def list(self) -> List[Station]:
        with open("D:/courses and slides/bdt-2021-master/src/stations.json", "r") as f:
            raw_stations = json.load(f)
            return [Station.from_repr(raw_station) for raw_station in raw_stations]




class SQLiteStationManager:

    DB_NAME = "station_snapshot.db"

    def save(self, stations: List[Station]) -> None:
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        query = "INSERT into station (station_id, name, address, lat, lon, city, slots, bikes, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        for station in stations:
            cursor.execute(query, (station.id, station.name, station.address, station.position.lat, station.position.lon, station.city, station.slots, station.bikes, station.dt.isoformat()))
            conn.commit() # Save (commit) the changes

        conn.close()

    def list(self) -> List[Station]:
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        query = "SELECT station_id, name, address, lat, lon, city, slots, bikes, timestamp from station"
        cursor.execute(query)
        rows = cursor.fetchall()

        stations = []
        for station_id, name, address, lat, lon, city, slots, bikes, timestamp in rows:
            stations.append(
                Station(
                    station_id,
                    name,
                    address, bikes, slots, city,
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
        query = "INSERT into 0518_0522bikesharing (station_id, name, address, lat, lon, city, slots, bikes, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for station in stations:
            cursor.execute(query, (
                station.id,
                station.name,
                station.address,
                station.position.lat,
                station.position.lon,
                station.city,
                station.slots,
                station.bikes,
                station.dt.isoformat()
            ))

        cursor.close()

    def list(self) -> List[Station]:
        cursor = self.connection.cursor()
        query = "SELECT station_id, name, address, lat, lon, city, slots, bikes, timestamp from station"
        cursor.execute(query)

        stations = []
        for station_id, name, address, lat, lon, city, slots, bikes, timestamp in cursor:
            stations.append(Station(
                station_id,
                name,
                address, bikes, slots, city,
                Position(lat, lon),
                datetime.fromisoformat(timestamp)
            ))

        cursor.close()

        return stations


