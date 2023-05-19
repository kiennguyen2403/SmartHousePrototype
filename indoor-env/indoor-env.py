from datetime import datetime
import json
import os

import paho.mqtt.client as paho
import serial
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

SERIAL_PORT = os.environ.get('SERIAL_PORT')

ser = serial.Serial()

SENSORS = ['temperature', 'humidity', 'smoke']
ACTIONS = {
    'fan': {
        True: b'0',
        False: b'1'
    },
    'heater': {
        True: b'2',
        False: b'3'
    },
    'buzzer': {
        True: b'4',
        False: b'5'
    }
}

MQTT_CONFIG = dict(
    host=os.environ.get('MQTT_HOST'),
    port=int(str(os.environ.get('MQTT_PORT'))),
    user=os.environ.get('MQTT_USER')
)
mqtt_client = paho.Client()

actuators = {
    'fan': False,
    'heater': False,
    'buzzer': False
}

sensors = {
    'temperature': 0,
    'humidity': 0,
    'smoke': 0
}


def on_connect(client, userdata, flags, rc, properties=None):
    print(f'Connected with result code {rc}.')


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print(f'Subscribed: {str(mid)} {str(granted_qos)}')


def on_message(client, userdata, msg):
    global actuator
    print(msg.topic, str(msg.qos), str(msg.payload), sep=' ')
    request_id = msg.topic.split('/')[-1]
    data = json.loads(msg.payload)
    if (msg.topic.startswith('v1/devices/me/rpc/request/')):
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
    mqtt_client = paho.Client(client_id='control1', userdata=None, protocol=paho.MQTTv5)
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
                print(f'Actuator {actuator} set to {actuators[actuator]} by IOT')
            for sensor in sensors:
                sensors[sensor] = data[sensor]

            print(json.dumps({ **actuators, **sensors }))

            mqtt_client.publish(
                'v1/devices/me/telemetry',
                payload=json.dumps({ **actuators, **sensors }),
                qos=1
            )
        except json.decoder.JSONDecodeError:
            print('Error: Invalid JSON')
            continue
