#!/usr/bin/python3
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

import serial

from influxdb import InfluxDBClient
# from local_conf import FLUXHOST, FLUXPORT, FLUXUSER, FLUXPASS, FLUXDBNM
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
path = os.path.dirname(__file__)
sys.path.append(path)
os.chdir(path)

# AAQS_SIZE = 82
AAQS_SIZE = 112

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
            'BMP_T': {'parameter': 'Temperature_P', 'measurement': '°C'.encode('UTF-8'), 'value': 0},
            'DHT_H': {'parameter': 'Humidity', 'measurement': '%', 'value': 0},
            'DHT_T': {'parameter': 'Temperature_H', 'measurement': '°C'.encode('UTF-8'), 'value': 0},
            }


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
    client = InfluxDBClient(FLUXHOST, FLUXPORT, FLUXUSER, FLUXPASS, FLUXDBNM)

    # sbuf = ''
    while True:
        finished = False
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        bbuf = bytearray()
        print("len bbuf: %s" % len(bbuf))
        while not finished:
            if ser.inWaiting() > 0:
                bbuf += ser.read(1)

            # print('sbuf_len: %s, sbuf: %s' % (len(sbuf), sbuf))
            if len(bbuf) == AAQS_SIZE:
                logger.debug("Finished reading data %s", bbuf)
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
            print("sbuf %s" % sbuf)
            lbuf = sbuf.split(', ')
            iso = int(time.time() * 1000000000)
            for i in lbuf:
                item = i.split(': ')
                print(item)
                if item[0] in ASENSORS:
                    data = [
                        {
                            "measurement": ASENSORS[item[0]]['measurement'],
                            "tags": {
                                "parameter": ASENSORS[item[0]]['parameter'],
                            },
                            "time": iso,
                            "fields": {
                                "value": float(item[1])
                            }
                        }
                    ]
                    print(data)
                    # # Send the JSON data to InfluxDB
                    client.write_points(data)
        time.sleep(60)
        # ser.reset_input_buffer()
        # ser.reset_output_buffer()


#################################################################################
if __name__ == "__main__":
    main()
