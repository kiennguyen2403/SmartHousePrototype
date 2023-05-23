import paho.mqtt.client as mqtt
import json


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe('v1/devices/me/rpc/response/+')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg)

def on_subscribe(client, userdata, mid, granted_qos):
    print()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.username_pw_set(username="5OTe93hoydyCvGJPdCae")
client.connect("130.162.195.45", 1883, 60)
client.loop_forever()

