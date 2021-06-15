import paho.mqtt.client as mqtt
import time

client = mqtt.Client() # when set the clientID means just publish one message one time,when not set it, could run a loop
client.username_pw_set("veratesttest","88888888")
client.connect(host="127.0.0.1", port = 1883, keepalive=10)
while True:
    print("777")
    client.publish(topic='bdt-2021/test', payload='666,777,888', qos=0, retain=True)
    time.sleep(2)
    print("666")
