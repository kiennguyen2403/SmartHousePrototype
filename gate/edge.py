import paho.mqtt.client as mqtt 
import datetime
import serial
import json
import threading
from dotenv import load_dotenv
import os


load_dotenv()
GATE_KEY = os.getenv("GATE_KEY")
HOST = os.getenv("HOST")
device = "/dev/cu.usbmodem21201"
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
        arduino.write(b'{"method":"OpenGate"}') # send OpenGate command to Arduino
    elif method == "ReturnWeatherData":
        arduinoCommand = {"method":"UpdateWeather","value":message["rain"]} 
        arduinoCommand = json.dumps(arduinoCommand)
        arduino.write(arduinoCommand.encode())  # send UpdateWeather command to Arduino
    elif method == "setValueBuzzer":
        arduinoCommand = json.dumps(message)
        arduino.write(arduinoCommand.encode())  # send setValueBuzzer command to Arduino


def on_subscribe(client, userdata, mid, granted_qos):
    pass
    
client = mqtt.Client() # create an MQTT client
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.username_pw_set(username=GATE_KEY)
client.connect(HOST, 1883, 60)
client.loop_start()

def getWeatherData():
    lastGetWeatherTime = datetime.datetime.now()
    while True:
        current_time = datetime.datetime.now()
        if (current_time - lastGetWeatherTime).seconds >= 200: # send a getWeather request every 200 seconds
            lastGetWeatherTime = current_time
            request = {
                    "method": "getWeather",
                    "params": {}
            }
            client.publish("v1/devices/me/rpc/request/1",json.dumps(request)) # get the new rain precipitation value for today

threading.Thread(target=getWeatherData).start() # start a new thread

while True:
    serialData = arduino.readline() # read data from serial line
    current_time = datetime.datetime.now() # get the current time
    decodedData = serialData.decode("utf-8")
    receivedData = json.loads(decodedData)
    receivedData["time"] = current_time.strftime("%Y-%m-%d %H:%M")
    if receivedData:
        print(receivedData)
        client.publish("v1/devices/me/telemetry",json.dumps(receivedData)) # publish a message to ThingsBoard



