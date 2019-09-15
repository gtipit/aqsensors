#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doc string.

Start Vnox: 115 Vred: 73 MQ135: 125 MQ131: 93 DHT_H: 45.10 DHT_T: 29.10 End
Start Vnox: 566, Vred: 76, MQ135: 133, MQ131: 98, DHT_H: 45.10, DHT_T: 29.50 End



"""
import os
import sys
import logging
import time
import socket

import serial

import paho.mqtt.client as mqtt

from local_conf import MQTTHOST, MQTTPORT, MQTTUSER, MQTTPASS, MQTTPUBT

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
path = os.path.dirname(__file__)
sys.path.append(path)
os.chdir(path)

# AAQS_SIZE = 82
AAQS_SIZE = 112

hostname = socket.gethostname()

SERIAL_DEVICE = '/dev/ttyUSB0'
serial_device = SERIAL_DEVICE

# FLUXHOST = '192.168.123.112'
FLUXHOST = '127.0.0.1'
FLUXPORT = 8086
FLUXUSER = 'asem'
FLUXPASS = 'mesa'

FLUXDBNM = 'aqsensors'

ASENSORS = {'Vnox': {'parameter': 'NOx', 'measurement': 'ppg', 'value': 0},
            'Vred': {'parameter': 'CO', 'measurement': 'ppg', 'value': 0},
            'MQ135': {'parameter': 'AQ', 'measurement': 'ppg', 'value': 0},
            'MQ131': {'parameter': 'O3', 'measurement': 'ppg', 'value': 0},
            'BMP_P': {'parameter': 'Pressure', 'measurement': 'gPa', 'value': 0},
            # 'BMP_T': {'parameter': 'Temperature_P', 'measurement': '°C'.encode('UTF-8'), 'value': 0},
            'BMP_T': {'parameter': 'Temperature_P', 'measurement': '°C', 'value': 0},
            'DHT_H': {'parameter': 'Humidity', 'measurement': '%', 'value': 0},
            # 'DHT_T': {'parameter': 'Temperature_H', 'measurement': '°C'.encode('UTF-8'), 'value': 0},
            'DHT_T': {'parameter': 'Temperature_H', 'measurement': '°C', 'value': 0},
            }

DEBUG = True


def main():
    """Doc string."""
    print('Hello!')
    logger = logging.getLogger(__name__)

    ser = serial.Serial(port=serial_device,
                        baudrate=9600,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS)
    ser.setDTR(False)
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
    mqttc.connect(MQTTHOST)

    # sbuf = ''
    start_sequence = 'Start'
    end_sequence = 'End'
    timeout = 20
    while True:
        si = 0
        ei = 0
        finished = False
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        bbuf = bytearray()
        char = ''
        print("len bbuf: %s" % len(bbuf))
        while not finished:
            if ser.inWaiting() > 0:
                char = ser.read(1)
                print(char,)
                if si < len(start_sequence):
                    # print(si),
                    if char.decode('UTF-8') == start_sequence[si]:
                        si += 1
                        bbuf += char
                    else:
                        si = 0
                        bbuf = bytearray()
                else:
                    # print('start ok!')
                    bbuf += char
                    if char.decode('UTF-8') == end_sequence[ei]:
                        ei += 1
                    else:
                        ei = 0
                    # print(ei)
                    if ei == len(end_sequence) or len(bbuf) > AAQS_SIZE:
                        #

                        print('bbuf_len: %s, bbuf: %s' % (len(bbuf), bbuf.decode('UTF-8')))

                        # logger.debug("Finished reading data %s", bbuf)
                        # Test Start-End simbols
                        sbuf = bbuf.decode('UTF-8').strip()
                        # finished = True
                        # print(sbuf[:5])
                        # print(sbuf[-3:])
                        if sbuf[:5].strip() == 'Start' and sbuf[-3:].strip() == 'End':
                            sbuf = sbuf[5:-3].strip()
                            print('test ok!')
                            finished = True
                        else:
                            print('Error!')
                            print(sbuf)
                            bbuf = bytearray()
                            break
        else:
            try:
                mqttc.connect(MQTTHOST)
            except Exception as e:
                pass
                print(e)
                # raise e
            print("sbuf %s" % sbuf)
            lbuf = sbuf.split(', ')
            iso = int(time.time() * 1000000000)
            for i in lbuf:
                item = i.split(': ')
                print(item)
                if item[0] in ASENSORS:
                    data = """{"%s": {"measurement": "%s", "tags": {"location": "%s", "parameter": "%s"}, "time": %s, "fields": {"value": %s}}}
                           """ % (item[0], ASENSORS[item[0]]['measurement'],
                                  hostname, ASENSORS[item[0]]['parameter'],
                                  iso, float(item[1]))
                    print(data.encode('UTF-8'))
                    try:
                        mqttc.publish(MQTTPUBT, payload=data, qos=0, retain=False)
                    except Exception as e:
                        pass
                        print(e)
                        # raise e
        mqttc.disconnect()
        time.sleep(59)
        # ser.reset_input_buffer()
        # ser.reset_output_buffer()


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


#################################################################################
if __name__ == "__main__":
    main()
