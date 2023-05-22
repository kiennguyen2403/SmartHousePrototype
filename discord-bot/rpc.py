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
client.username_pw_set(username=os.getenv('DISCORD_BOT_ACCESS_KEY'))
client.connect(os.getenv('MQTT_HOST'), 1883, 60)
client.loop_start()

def sendMessage(method,id):
    print("Fire message")
    request = {
                    "method": method,
                    "params": {}
            }
    client.publish("v1/devices/me/rpc/request/"+str(id),json.dumps(request))
    
