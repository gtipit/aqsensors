#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MH-Z19.

Get data and store to influx db.
"""
import os
import sys
import logging
import time
import socket
# from pmsensor import serial_data_collector as pm
# from pmsensor import serial_pm as pm
from pmsensor import co2sensor
from pmsensor import serial_pm as pm

import paho.mqtt.client as mqtt


from local_conf import MQTTHOST, MQTTPORT, MQTTUSER, MQTTPASS, MQTTPUBT

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# from datetime import datetime
#
# from local_conf import SOURDEST
##
path = os.path.dirname(__file__)
sys.path.append(path)
os.chdir(path)

hostname = socket.gethostname()

DEBUG = True


def main():
    """Doc string."""
    logging.basicConfig(level=logging.INFO)

    # ppm = co2sensor.read_mh_z19("/dev/ttyS2")
    # print("CO2 concentration is {} ppm".format(ppm))
    # print(co2sensor.read_mh_z19_with_temperature("/dev/ttyS2"))
    # print("CO2 concentration is {} ppm".format(ppm))
    # client = InfluxDBClient(FLUXHOST, FLUXPORT, FLUXUSER, FLUXPASS, FLUXDBNM)

    mqttc = mqtt.Client()
    mqttc.username_pw_set(MQTTUSER, MQTTPASS)

    # mqttc.on_message = on_message
    # mqttc.on_connect = on_connect
    # mqttc.on_publish = on_publish
    # mqttc.on_subscribe = on_subscribe

    # Uncomment to enable debug messages
    if DEBUG:
        mqttc.on_log = on_log
    # mqttc.connect("localhost", 1883, 60)
    # mqttc.connect(MQTTHOST)
    # mqttc.subscribe(inp_topics)

    mqttc.connect(MQTTHOST)

    while True:

        try:
            mqttc.connect(MQTTHOST)
        except Exception as e:
            # pass
            # raise e
            print(e)

        # print(s.read_data())
        iso = int(time.time() * 1000000000)
        ppm = co2sensor.read_mh_z19("/dev/ttyS2")
        print("CO2 concentration is {} ppm".format(ppm))
        measurement = 'ppm'
        if ppm is not None:
            data = """{"MH-Z19B": {"measurement": "%s", "tags": {"location": "%s", "parameter": "CO2"}, "time": %s, "fields": {"value": %s}}}
                   """ % (measurement, hostname, iso, ppm)
            print(data)
        #     # # Send the JSON data to InfluxDB
        #     client.write_points(data)
        try:
            mqttc.publish(MQTTPUBT, payload=data, qos=0, retain=False)
        except Exception as e:
            pass
            # raise e
            print(e)
        # time.sleep(60)
        pms = pm.PMDataCollector("/dev/ttyS1", pm.SUPPORTED_SENSORS["plantower,pms1003"])
        sdata = pms.read_data()
        print(sdata)
        measurement = 'ug/m3'

        for i in sdata:
            print(i, sdata[i])
            data = """{"PMS1003": {"measurement": "%s", "tags": {"location": "%s", "parameter": "%s"}, "time": %s, "fields": {"value": %s}}}
                   """ % (measurement, hostname, i, iso, sdata[i])
            print(data)
            try:
                mqttc.publish(MQTTPUBT, payload=data, qos=0, retain=False)
            except Exception as e:
                pass
                # raise e
                print(e)
            time.sleep(1)
        # mqttc.disconnect()
        time.sleep(57)


def on_publish(mqttc, obj, mid):
    """Doc string."""
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    """Doc string."""
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    """Doc string."""
    print(string)

    # def getnom(psource=11, ptype=4, parnom=0):


if __name__ == '__main__':
    main()
