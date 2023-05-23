import paho.mqtt.client as mqtt
import json
from time import sleep
import datetime
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe('v1/devices/me/rpc/response/+')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode("utf-8"))
    print(message)



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username="Mpn8DENz7vSYHemvFpIi")
client.connect("130.162.195.45", 1883, 60)
import threading
def getWeatherData():
    lastGetWeatherTime = datetime.datetime.now()
    while True:
        current_time = datetime.datetime.now()
        if (current_time - lastGetWeatherTime).seconds == 5:
            lastGetWeatherTime = current_time
            request = {
                    "method": "OpenGate",
                    "params": {}
            }
            client.publish("v1/devices/me/rpc/request/1",json.dumps(request))

threading.Thread(target=client.loop_forever).start()
threading.Thread(target=getWeatherData).start()

