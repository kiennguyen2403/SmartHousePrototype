from datetime import datetime
import json
import os

import paho.mqtt.client as paho
import serial
from dotenv import load_dotenv

load_dotenv()

SERIAL_PORT = os.getenv('SERIAL_PORT')



ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)

SENSORS = ["ultrasonic"]
ACTIONS = {
    "light": {
        True: b'0',
        False: b'1'
    },
    "servo": {
        True: b'2',
        False: b'3'
    }
}

MQTT_CONFIG = dict(
    host=os.getenv('MQTT_HOST'),
    port=int(os.getenv('MQTT_PORT')),
    user=os.getenv('MQTT_USER')
)


actuators = {
    'light': False,
    'servo': False
}

sensors = {
    'distancePrevious': [],
    'distanceCurrent': [],
    'timer': 0
}


def on_connect(client, userdata, rc, *extra_params):
    print("Connected to MQTT broker with result code "+str(rc))
    print("Subscribed to topic")
    client.subscribe('v1/devices/me/rpc/request/+', 1)

def on_message(client, userdata, msg):
    global actuators
    request_id = msg.topic.split('/')[-1]
    data = json.loads(msg.payload)
    print(f'Received message: {data}')
    if (msg.topic.startswith('v1/devices/me/rpc/request/')):
        actuator = data['method'].split('Value')[-1].lower()
        if (actuator):
            if data['method'].startswith('setValue'):
                actuators[actuator] = data['params']
                print(f'Actuator {actuator} set to {actuators[actuator]}')
                ser.write(ACTIONS[actuator][actuators[actuator]])

            if data['method'].startswith('getValue'):
                print(f'Actuator {actuator} is {actuators[actuator]}')
                client.publish(
                    f'v1/devices/me/rpc/response/{request_id}',
                    payload='true' if actuators[actuator] else 'false',
                    qos=1
                )
            
            client.publish(
                f'v1/devices/me/rpc/response/{request_id}',
                payload='true' if actuators[actuator] else 'false',
                qos=1
            )
        else:
            if data['method'].startswith('setValue'):
                print(f'All actuators set to {data["params"]}')
                ser.write(ACTIONS["light"][data['params']])
                ser.write(ACTIONS["servo"][data['params']])
                client.publish(
                    f'v1/devices/me/rpc/response/{request_id}',
                    payload='true' if data['params']== 'true' else 'false',
                    qos=1)

def setup_mqtt():
    global mqtt_client
    mqtt_client = paho.Client(client_id='control1',
                              userdata=None, protocol=paho.MQTTv5)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(MQTT_CONFIG['user'])
    mqtt_client.connect(MQTT_CONFIG['host'], MQTT_CONFIG['port'], keepalive=60)
    mqtt_client.loop_start()


print('Starting edge device...')
setup_mqtt()

while True:
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    if not line:
        continue

    try:
        data = json.loads(line)
        for actuator in actuators:
            actuators[actuator] = data[actuator]
    
        for sensor in sensors:
            sensors[sensor] = data[sensor]



        mqtt_client.publish(
            'v1/devices/me/telemetry',
            payload=json.dumps({**actuators, **sensors}),
            qos=1
        )
    except json.decoder.JSONDecodeError:
        print('Error: Invalid JSON')
        continue
