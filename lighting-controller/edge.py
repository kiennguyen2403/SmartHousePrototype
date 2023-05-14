from datetime import datetime
import json
import os

import paho.mqtt.client as paho
import serial

SERIAL_PORT = os.getenv('SERIAL_PORT')

ser = serial.Serial()
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
    host=os.environ.get('MQTT_HOST'),
    port=int(os.environ.get('MQTT_PORT')),
    user=os.environ.get('MQTT_USER')
)

mqtt_client = paho.Client()

actuators = {
    'light': False,
    'servo': False
}

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic")
    for sensor in SENSORS:
        client.subscribe(f"sensor/{sensor}")

    for actuator in actuators:
        client.subscribe(f"actuator/{actuator}")

def on_message(client, userdata, msg):
    global actuators
    request_id = msg.topic.split('/')[-1]
    data = json.loads(msg.payload)
    if (msg.topic.startswith('sensor')):
        actuator = data['method'].split('Value')[-1].lower()
        if data['method'].startswith('setValue'):
            actuators[actuator] = data['params']
            print(f'Actuator {actuator} set to {actuators[actuator]}')
            ser.write(ACTIONS[actuator][actuators[actuator]])

        client.publish(
            f'v1/devices/me/rpc/response/{request_id}',
            payload='true' if actuators[actuator] else 'false',
            qos=1
        )


def setup_mqtt():
    global mqtt_client
    mqtt_client = paho.Client(client_id='control1',
                              userdata=None, protocol=paho.MQTTv5)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(MQTT_CONFIG['user'])
    mqtt_client.connect(MQTT_CONFIG['host'], MQTT_CONFIG['port'], keepalive=60)
    mqtt_client.subscribe('v1/devices/me/rpc/request/+', 1)
    mqtt_client.loop_start()


if __name__ == '__main__':
    print('Starting edge device...')
    setup_mqtt()

    ser = serial.Serial(SERIAL_PORT, 115200)

    while True:
        line = ser.readline().decode('utf-8').rstrip()
        if not line:
            continue

        try:
            data = json.loads(line)

            for actuator in actuators:
                actuators[actuator] = data[actuator]
                print(
                    f'Actuator {actuator} set to {actuators[actuator]} by IOT')
            for sensor in sensors:
                sensors[sensor] = data[sensor]

            print(json.dumps({**actuators, **sensors}))

            mqtt_client.publish(
                'v1/devices/me/telemetry',
                payload=json.dumps({**actuators, **sensors}),
                qos=1
            )
        except json.decoder.JSONDecodeError:
            print('Error: Invalid JSON')
            continue
