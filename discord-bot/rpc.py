import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from GPTWrapper import ask
import os
import json
load_dotenv()

def on_connect(client, userdata, flags, rc):
    print('connected')
    client.subscribe("v1/devices/me/rpc/request/+")
  
def on_message(client, userdata, msg):
    message = json.loads(msg.payload.decode("utf-8"))
    print(message)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


# def openGate():
#     print("vao open gate")
#     client.username_pw_set(username=os.getenv('GATE_ACCESS_KEY'))
#     client.connect(os.getenv('MQTT_HOST'), 1883, 60)
#     request = {
#                     "method": "OpenGate",
#                     "params": {}
#             }
#     client.publish("v1/devices/me/rpc/request/1",json.dumps(request))
#     client.loop_start()

# def closeGate():
#     print("vao close gate")
#     client.username_pw_set(username=os.getenv('GATE_ACCESS_KEY'))
#     client.connect(os.getenv('MQTT_HOST'), 1883, 60)
#     request = {
#                     "method":"CloseGate",
#                     "params": {}
#     }



def sendMessage(method, request,id):
    print("Fire message")
    client.username_pw_set(username=os.getenv('GATE_ACCESS_KEY'))
    client.connect(os.getenv('MQTT_HOST'), 1883, 60)
    request = {
                    "method": method,
                    "params": {}
            }
    client.publish("v1/devices/me/rpc/request/"+str(id),json.dumps(request))
    client.loop_start()

