import sqlite3
from sqlite3.dbapi2 import connect
import mysql.connector


conn = sqlite3.connect("station_snapshot.db")
cursor = conn.cursor()
query_0 = "SELECT * from station;"
query_1 = "SELECT name,station_id from station"
cursor.execute(query_1)

rows = cursor.fetchall()
print(rows)
for (name, station_id) in rows:
    print(f"{station_id}: {name}")

query_2 = "INSERT into station(id, station_id, name, address, lat, lon, city, slots, bikes, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
cursor.execute(query_2, (4, "station_2", "station 2", "address", 12, 12, "Trento", 12, 21, "2021-05-20T13:00:00"))  ## must add the para ID
conn.commit()
# print(rows)
# for (name, station_id) in rows:
#     print(f"{station_id}: {name}")
conn.close()


connection = mysql.connector.connect(host = "localhost", 
    port = 3306,
    database = "bdt_station",
    user = "root",
    password = "root")
print("----")
cursor = connection.cursor()
connection.autocommit = True
query_0 = "INSERT into station (station_id, name, address, lat, lon, city, slots, bikes, timestamp) VALUES (1, 2, 3, 4, 5, 6, 7, 8, 20210210124000);"
cursor.execute(query_0)

query_1 = "SELECT id from station"
cursor.execute(query_1)
for (i,) in cursor:
    print(i)

cursor.close()
connection.close()
