from __future__ import print_function

import os
import time

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTT_ERR_SUCCESS, MQTT_ERR_NO_CONN

def connect_mqtt(host, port, username, password):
    mqttc = mqtt.Client()
    mqttc.username_pw_set(username, password)
    print("Connecting to {}".format(host))
    mqttc.connect(host, port, 60)
    print("Connected")
    mqttc.loop_start()
    mqttc.on_disconnect = on_disconnect
    return mqttc


def disconnect_mqtt(mqttc):
    mqttc.loop_stop()
    mqttc.disconnect()


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        client.reconnect()


def publish_temp(mqttc, thermometer, temp):
    topic = "raspberry-pi/w1/thermometer/{}".format(thermometer)
    (result, mid) = mqttc.publish(topic, temp)
    if result == MQTT_ERR_SUCCESS:
        print("Published {} to {}".format(temp, topic))
    elif result == MQTT_ERR_NO_CONN:
        print("Connection error")
    else:
        print("Unknown error")