import paho.mqtt.client as mqtt
import datetime
import serial
import json
import threading
import random
device = "/dev/cu.usbmodem21301"
arduino = serial.Serial(device,9600)
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe("v1/devices/me/rpc/request/+")
    client.subscribe('v1/devices/me/rpc/response/+')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode("utf-8"))
    print(message)
    method = message.get("method",None)
    if  method == "OpenGate":
        arduino.write(b'{"method":"OpenGate"}')
    elif method == "ReturnWeatherData":
        arduinoCommand = {"method":"UpdateWeather","value":message["rain"]}
        arduinoCommand = json.dumps(arduinoCommand)
        print(arduinoCommand)
        arduino.write(arduinoCommand.encode())
    elif method == "setValueBuzzer":
        arduinoCommand = json.dumps(message)
        arduino.write(arduinoCommand.encode())


def on_subscribe(client, userdata, mid, granted_qos):
    print( )

    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.username_pw_set(username="5OTe93hoydyCvGJPdCae")
client.connect("130.162.195.45", 1883, 60)


def getWeatherData():
    lastGetWeatherTime = datetime.datetime.now()
    while True:
        current_time = datetime.datetime.now()
        if (current_time - lastGetWeatherTime).seconds == 100:
            lastGetWeatherTime = current_time
            request = {
                    "method": "getWeather",
                    "params": {}
            }
            client.publish("v1/devices/me/rpc/request/1",json.dumps(request))

threading.Thread(target=client.loop_forever).start()
threading.Thread(target=getWeatherData).start()

while True:
    current_time = datetime.datetime.now()
    serialData = arduino.readline()
    decodedData = serialData.decode("utf-8")
    receivedData = json.loads(decodedData)
    receivedData["time"] = current_time.strftime("%Y-%m-%d %H:%M")
    if receivedData:
        print(receivedData)
        client.publish("v1/devices/me/telemetry",json.dumps(receivedData))



