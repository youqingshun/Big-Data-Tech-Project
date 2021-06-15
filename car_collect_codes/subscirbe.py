from station import Station, MySQLStationManager
import paho.mqtt.client as mqtt
import time
import json



def when_message_received_to_do_this(client, user_data, msg):
    # print(msg) # output is : <paho.mqtt.client.MQTTMessage object at 0x000002341A2B5C10>
    # print(msg.payload) # output is : b'666,777,888'
    str_station = msg.payload.decode()
    print(str_station)
    # print(msg.payload.decode()) # output is : 666,777,888 
   
client = mqtt.Client() # when set the clientID means just publish one message one time,when not set it, could run a loop
client.username_pw_set("veratesttest","88888888")
client.on_message = when_message_received_to_do_this

client.connect(host="127.0.0.1", port = 1883, keepalive=10)
client.subscribe("bdt-2021/Trento/station")
client.loop_forever()
